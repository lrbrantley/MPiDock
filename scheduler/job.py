from enum import Enum
import json

class JobType(Enum):
    LAB = "Lab127"
    CLUSTER = "Bishop Cluster"

    def __str__(self):
        return self.value

STRING_FORMAT = "Job: {} Options: {} JobId: {} Start: {}"


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JobType):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class Job:
    # Jobs are assumed to attempt to run every day.
    def __init__(self, job, jobOptions, jobId, startHour, duration = None):
        self.job = job
        self.jobId = jobId
        self.jobOptions = jobOptions
        self.start = startHour
        self.duration = duration

    def __str__(self):
        jobString = STRING_FORMAT.format(self.job, self.jobOptions, self.jobId, self.start);
        if self.duration is not None:
            jobString += " Duration: " + str(self.duration)
        return jobString
##        seq = [str(self.job), self.jobOptions, self.jobId, str(self.start)]
##        if self.duration is not None:
##            seq.append(str(self.duration))
##        return " ".join(seq)

    def toJSON(self):
        return json.dumps(self.__dict__, cls=EnumEncoder)

def jobFromString(s):
    return Job(*s.split())
    
