def STRING_FORMAT = "Job: {} Options: {} JobId: Start: {}"

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
        seq = [self.job, self.jobOptions, self.jobId, str(self.start)]
        if self.duration is not None:
            seq.append(str(self.duration))
        return " ".join(seq)

def jobFromString(s):
    return Job(*s.split())
    
