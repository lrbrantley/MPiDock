#!/usr/bin/env python3
from os import path
from job import Job, JobType, jobFromJSON
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
    for j in jobL:
        print(str(j))

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
    performList()
    



def handleDelete():
    print("not yet implemented")

def handleModify():
    print("not yet implemented")


def main():
   processOption()
    

if __name__ == "__main__":
    main()
