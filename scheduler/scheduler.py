#!/usr/bin/env python3
from os import path
from job import Job, jobFromJSON, CRON_JOB_ID_TAG
import subprocess
import uuid

## TODO: Remove timeout option from scheduler, it's not well implemented with how the complete system works...

OPTION_MENU = """\
Hello, what would you like to do?
    1. List existing jobs
    2. Create a new job
    3. Delete an existing job
    4. Modify an existing job
    5. Exit
"""
VALID_OPTIONS = ["1", "2", "3", "4", "5"]

JOBS_FILE = "scheduledjobs.txt"


def readJobFile():
    with open(JOBS_FILE, "a+") as f:
        f.seek(0)
        return f.read()


def parseJobFile():
    jobText = readJobFile().split("\n")
    return [jobFromJSON(x) for x in jobText if x]


def writeJobFile(s):
    with open(JOBS_FILE, "w") as f:
        f.write(s)


def writeJobsToJobFile(jl):
    s = '\n'.join([j.toJSON() for j in jl]) + '\n'
    writeJobFile(s)


def processOption():
    choice = ""
    while True:
        choice = input(OPTION_MENU).strip()
        if choice == "1":
            performList()
        elif choice == "2":
            handleCreate()
        elif choice == "3":
            handleDelete()
        elif choice == "4":
            handleModify()
        elif choice == "5":
            return
        else:
            print("Invalid Choice Entered, Please Select Another")

## performList prints out the existing jobs
## TODO: Should this attempt to syncronize with crontab??
def performList():
    jobL = parseJobFile()
    i = 1
    print('Current Jobs')
    for j in jobL:
        print('Job ' + str(i) + ': ' + str(j))
        i += 1
    print()


def getValidHour():
    hour = -1
    while hour < 0 or hour > 23:
        hour = int(input('Please input a time between 0 and 23\n').strip())
    return int(hour)


def getEndTime():
    inputS = input("Which hour (0 - 23) would you like the job to end? -1 to run to completion\n").strip()
    return int(inputS)


def calculateTimeout(start, end):
    if 0 <= end <= 23:
        if end < start:
            end += 24
        return end - start   
    else:
        return None


def getJobLocation():
    jobLoc = input('Please input the location of the job you would like to run\n')
    return jobLoc.strip()

## handleCreate creates a new job.
## Internally it should create a new job object, then place it into the crontab
##   and the JOBS_FILE
def handleCreate():
    start = getValidHour()
    print("Start set to " + str(start))

    end = getEndTime()
    timeout = calculateTimeout(start, end)
    if timeout == None:
        print("Job set to run until completion")
    else:
        print("Job set to run for " + str(timeout) + " hours")

    jobId = uuid.uuid4().hex
    
    jobLoc = getJobLocation()
    ## Defaults to just making lab127 jobs atm.
    ## Also defaults to no options at the moment
    job = Job(jobLoc, "", jobId, start, timeout)

    currentJobs = readJobFile()
    currentJobs += job.toJSON() + "\n"
    writeJobFile(currentJobs)
    writeJobToCrontab(job)
    performList()
   

def writeToCrontab(cronStr):
    process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    stdOutErr = process.communicate(bytes(cronStr, 'utf-8'))
    if process.returncode:
        print("FAILED TO WRITE CRONTAB\n" + stdOutErr[1].decode())


def readCrontab():
    crontab = None
    try:
        crontab = subprocess.check_output(['crontab', '-l']).decode()
    except subprocess.CalledProcessError as e:
        ## THIS SEEMS TO BE PRINTING CRAP... Capture stderr and see if was just no crontab issue
        ## TODO: squelch no crontab error
        crontab = ""
    return crontab 


def writeJobToCrontab(job):
    currentCrontab = readCrontab()
    newCrontab = currentCrontab + job.cronStr() + '\n'
    writeToCrontab(newCrontab)    


def findJobFromCrontab(crontab, jobId):
    lineNum = None
    for i in range(len(crontab)):
        line = crontab[i]
        for j in range(len(line)):
            if line[j] == CRON_JOB_ID_TAG:
                if line[j + 1] == jobId:
                    if lineNum:
                        raise RuntimeError("More than one job with the same jobId in crontab!!")
                    else:
                        lineNum = i

    if lineNum is None:
        ## TODO: Provide syncronization option?
        print('Job Id ' + jobId + ' not found within crontab!')
        return None
    return lineNum


def deleteJobFromCrontab(crontab, job):
    cronlines = crontab.splitlines()
    wsSplitCrontab = [x.split() for x in cronlines]
    jobLine = findJobFromCrontab(wsSplitCrontab, job.jobId)
    if jobLine is None:
        return

    del cronlines[jobLine]
    newCrontab = ''
    if len(cronlines):
        newCrontab = '\n'.join(cronlines) + '\n'
    writeToCrontab(newCrontab)


## Reads out existing jobs, and lets the user choose from them. Returns the Job chosen.
def chooseFromExistingJobs(currentJobs):
    if not currentJobs:
        print("There are no existing jobs\n")
        return

    numJobs = len(currentJobs)

    choice = None
    while not choice:
        print('Which existing job would you like to delete?')
        print('Choose a job below or type \'quit\'')
        performList()
        choice = input()
        if choice.lower() == 'quit':
            return
        numChoice = int(choice)
        if numChoice <= 0 or numChoice > numJobs:
            print('Job chosen does not exist\n')
            choice = None

    return (currentJobs[numChoice - 1], numChoice - 1)


def handleDelete():
    currentJobs = parseJobFile()
    jobToDelete, choice = chooseFromExistingJobs(currentJobs)
    if not jobToDelete:
        return

    currentCrontab = readCrontab()
    if not currentCrontab:
        print('Crontab is empty. Nothing to delete.\n')
        return

    deleteJobFromCrontab(currentCrontab, jobToDelete)
    del currentJobs[choice]
    writeJobsToJobFile(currentJobs)
    print('Job Deleted')
    performList()


def getModifications(job):
    print('Job\'s current settings: ' + str(job))
    while True:
        choice = input(('Choose what you would like to modify or type \'done\'.\n'
                        '1. Start Time\n'
                        '2. End Time\n'
                        '3. Job Config Location\n')).strip()
        if choice == '1':
            time = getValidHour()
            job.start = time
        elif choice == '2':
            end = getEndTime()
            timeout = calculateTimeout(job.start, end)
            job.duration = timeout
        elif choice == '3':
            jobLoc = getJobLocation()
            job.job = jobLoc
        elif choice == 'done':
            return
        else:
            print('Invalid option entered.')


def modifyJobInCrontab(crontab, job):
    cronlines = crontab.splitlines()
    wsSplitCrontab = [x.split() for x in cronlines]
    jobLine = findJobFromCrontab(wsSplitCrontab, job.jobId)
    if jobLine is None:
        return
    print('Job within modify in crontab ' + str(job))
    cronlines[jobLine] = job.cronStr()
    newCrontab = '\n'.join(cronlines) + '\n'
    writeToCrontab(newCrontab)


def handleModify():
    currentJobs = parseJobFile()
    jobToModify, choice = chooseFromExistingJobs(currentJobs)
    if not jobToModify:
        return

    currentCrontab = readCrontab()
    if not currentCrontab:
        print('Crontab is empty. Nothing to delete.\n')
        return

    getModifications(jobToModify)
    print('Job after mods: ' + str(jobToModify))
    currentJobs[choice] = jobToModify
    modifyJobInCrontab(currentCrontab, jobToModify)
    writeJobsToJobFile(currentJobs)
    performList()


def main():
   processOption()
    

if __name__ == "__main__":
    main()
