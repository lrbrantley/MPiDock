#!/usr/bin/env python3
from os import path
from job import Job, JobType, jobFromJSON, CRON_JOB_ID_TAG
import subprocess
import uuid


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
    s = '\n'.join([j.toJSON for j in jl]) + '\n'
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
def performList():
    jobL = parseJobFile()
    i = 1
    for j in jobL:
        print('Job ' + str(i) + ': ' + str(j))
        i += 1

## handleCreate creates a new job.
## Internally it should create a new job object, then place it into the crontab
##   and the JOBS_FILE
def handleCreate():
    start = -1
    while (start < 0 or start > 23):
        inputS = input("Which hour (0 - 23) would you like to start?\n")
        start = int(inputS)

    print("Start set to " + str(start))

    inputS = input("Which hour (0 - 23) would you like the job to end? -1 to run to completion\n")
    end = int(inputS)
    timeout = None
    if 0 <= end <= 23:
        if end < start:
            end += 24
        timeout = end - start

    if timeout == None:
        print("Job set to run until completion\n")
    else:
        print("Job set to run for " + str(timeout) + " hours\n")

    jobId = uuid.uuid4().hex
    
    ## Defaults to just making lab127 jobs atm.
    ## Also defaults to no options at the moment
    job = Job(JobType.LAB, "", jobId, start, timeout)

    currentJobs = readJobFile()
    currentJobs += job.toJSON() + "\n"
    writeJobFile(currentJobs)
    writeJobToCrontab(job)
    performList()
    
def writeToCrontab(cronStr):
    process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    stdOutErr = process.communicate(bytes(newCrontab, 'utf-8'))
    if not process.returncode:
        print("FAILED TO WRITE CRONTAB\n" + stdOutErr[1])


def readCrontab():
    crontab = None
    try:
        crontab = subprocess.check_output(['crontab', '-l']).decode()
    except subprocess.CalledProcessError as e:
        crontab = ""
    return crontab 


def writeJobToCrontab(job):
    currentCrontab = readCrontab()
    newCrontab = currentCrontab + job.cronStr() + '\n'
    writeToCrontab(newCrontab)    


def findJobFromCrontab(crontab, jobId):
    lineNum = None
    for i in len(crontab):
        for j in len(crontab[i]):
            if line[j] == CRON_JOB_ID_TAG:
                if line[j + 1] == jobId:
                    if lineNum:
                        raise RuntimeError("More than one job with the same jobId in crontab!!")
                    else:
                        lineNum = j + 1

    if not lineNum:
        raise RuntimeError('No job with job id: ' + jobId + ' found within crontab!\n')
    return lineNum


def deleteJobFromCrontab(crontab, job):
    wsSplitCrontab = [x.split() for x in crontab]
    jobLine = findJobFromCrontab(wsSplitCrontab, job.jobId)
    crontab.del(jobLine)
    newCrontab = '\n'.join(crontab) + '\n'
    writeToCrontab(newCrontab)

def handleDelete():
    currentCrontab = None
    try:
        currentCrontab = subprocess.check_output(['crontab', '-l']).decode()
    except subprocess.CalledProcessError as e:
        print('There are no jobs in the crontab\n')
        return
    cronLines = currentCrontab.split('\n')

    currentJobs = parseJobFile()
    if not currentJobs:
        print("There are no existing jobs\n")
        return
    numJobs = len(currentJobs)

    choice = None
    while not choice:
        print('Which existing job would you like to delete?\n')
        choice = input(performList())
        if (choice <= 0 || choice > numJobs)
            print('Job chosen does not exist\n')
            choice = None

    jobToDelete = currentJobs[choice - 1]
    deleteJobFromCrontab(currentCrontab, jobToDelete)
    currentJobs.del(choice - 1)
    writeJobsToJobFile(currentJobs)
    performList()


def handleModify():
    
    print("not yet implemented")


def main():
   processOption()
    

if __name__ == "__main__":
    main()
