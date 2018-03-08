from enum import Enum
import json

STRING_FORMAT = "Job: {} Options: {} JobId: {} Start: {}"
CRON_JOB_ID_TAG = '--jobid'
##             M  H  D  M DOW CMD JOB_ID
CRON_FORMAT = '{} {} {} {} {} {} ' + CRON_JOB_ID_TAG + ' {}'

class Job:
    # Jobs are assumed to attempt to run every day.
    def __init__(self, job, jobOptions, jobId, startHour):
        self.job = job
        self.jobId = jobId
        self.jobOptions = jobOptions
        self.start = startHour

    def __str__(self):
        return STRING_FORMAT.format(self.job, self.jobOptions, self.jobId, self.start);
        
    def toJSON(self):
        return json.dumps(self.__dict__, sort_keys=True)

    def cronStr(self):
        return CRON_FORMAT.format(0, self.start, "*", "*", "*", self.job, self.jobId)
        

def jobFromJSON(jsonS):
    jsonO = json.loads(jsonS)
    job = jsonO["job"]
    jobOptions = jsonO["jobOptions"]
    jobId = jsonO["jobId"]
    start = jsonO["start"]
    return Job(job, jobOptions, jobId, start)
