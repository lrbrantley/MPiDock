#!/usr/bin/env python3
import argparse
import datetime
import logging
import logging.handlers
import os
import shutil
import subprocess
import tempfile
import time

LOGGER = None
ERROR_BANNER = '///// ERROR /////'

processedDirPrefix = 'Processed'
startTime = None
timeLimit = None

parser = argparse.ArgumentParser()
parser.add_argument('command', help='Location of command on local machine to execute remotely')
parser.add_argument('ssh', help='User and Remote SSH Address or an alias')
parser.add_argument('remote', help='Location on remote machine')
parser.add_argument('-i', '--input',
        help='Location for input files. These will be transfered')
parser.add_argument('-o', '--output',
        help='Location for output files. Remote output will be transfered back into this folder')
parser.add_argument('-b', '--batch',
        help='Number of input files to transfer per usage. Defaults to all of them')
parser.add_argument('-t', '--timeout',
        help='Time limit in HOURS for batches to run. After time limit is reached no further batches will be sent.\
        Also implicitly sends the remaining time as an argument to whatever command is running.')
parser.add_argument('-args', '--arguments',
        help='Arguments to send to remote command')
parser.add_argument('-mdir', '--miscdir', help='Location of extra directory to send over.')
parser.add_argument('-v', '--verbose', help='Verbose printing. Currently not in use.')
parser.add_argument('--processedPrefix', help='If your processed files have a prefix, use this argument to specify what the prefix is. That way files can be moved to the processed directory appropriately.')
parser.add_argument('--processedFilesModified', action='store_true', help='Use this flag to specify if input files are modified remotely before placing in processed directory. This will transfer them back rather than moving files over.')

args, __ = parser.parse_known_args()

def getRsyncPath():
    return args.ssh + ':' + args.remote

def pathBasename(p):
    return os.path.basename(os.path.normpath(p))

## buildPkg makes a temporary directory with files to be sent. Returns absolute path of temp dir.
def buildPkg(cmdPath, inputFiles = []):
    tempDir = tempfile.mkdtemp()
    shutil.copy2(cmdPath, tempDir)

    if args.input:
        inputDirName = pathBasename(args.input)
        os.mkdir(tempDir + '/' + inputDirName)
        for inF in inputFiles:
            fileP = args.input + '/' + inF
            try:
                shutil.copy2(fileP, tempDir + '/' + inputDirName)
            except FileNotFoundError as e:
                LOGGER.warn(ERROR_BANNER);
                LOGGER.error('File %s could not be added to package because it was not found.'
                             ' Check to see if it is already processed.', inF)
        os.mkdir(tempDir + '/' + processedDirPrefix + inputDirName)

    if args.output:
        os.mkdir(tempDir + '/' + pathBasename(args.output))
    
    if args.miscdir:
        shutil.copytree(args.miscdir, tempDir + '/' + pathBasename(args.miscdir))
        
    return tempDir


## Performs rsync with some retries, just in case.
def rsyncWrapper(src, dest):
    error = None
    for i in range(5):
        try:
            subprocess.check_output(['rsync', '-avz', src, dest], stderr=subprocess.PIPE)
            return
        except subprocess.CalledProcessError as e:
            LOGGER.warn(ERROR_BANNER);
            LOGGER.error('Failed to retrieve output files on attempt %s\n'
                         'Command: %s\n'
                         'Return Code: %s\n'
                         'stdout: %s\n'
                         'stderr: %s\n',
                         str(i),
                         e.cmd,
                         e.returncode,
                         e.stdout.decode(),
                         e.stderr.decode())
            error = e
    ## If it fails after 5 tries, we have to quit.
    raise error


## Sends package over.
def sendPkg(tempDir):
    rsyncWrapper(tempDir + '/', getRsyncPath())


## Removes the temp local package.
def cleanupTempPkg(tempDir):
    shutil.rmtree(tempDir)


## Executes the given command remotely.
## Returns True if executes successfully, False otherwise.
def execRemoteCmd():
    timeRemaining = None
    if timeLimit is not None:
        timeRemaining = startTime + timeLimit - time.monotonic()
    if timeRemaining is not None and timeRemaining < 0:
        return

    cmdArgs = args.arguments
    if cmdArgs is None:
        cmdArgs = ''

    if timeRemaining:
        cmdArgs += ' -t ' + str(timeRemaining)

    sshcmd = ['ssh', args.ssh, 'bash']
    heredoc = ('<< EOF\n'
               'cd ' + args.remote + '\n'
               './' + pathBasename(args.command) + ' ' + cmdArgs + '\n'
               'EOF')
    sshcmd.append(heredoc)
    try:
        cmdOut = subprocess.check_output(sshcmd, stderr=subprocess.PIPE).decode()
        LOGGER.info('command finished with output:\n'
                    '%s',
                    cmdOut)
        return True
    except subprocess.CalledProcessError as e:
        LOGGER.warn(ERROR_BANNER);
        LOGGER.warn('command raised a non zero exit code\n'
                    'CMD: %s\n'
                    'Exit Code: %s\n'
                    'stdout: %s\n'
                    'stderr: %s\n',
                    e.cmd,
                    e.returncode,
                    e.stdout.decode(),
                    e.stderr.decode())
        return False


## If there's a prefix, remove it to figure out the input file.
def getCorrespondingInputFile(processedFile):
    prefix = args.processedPrefix
    if prefix is not None and processedFile.startswith(prefix):
        return processedFile[len(prefix):]
    else:
        return processedFile


## Check for files in the remote processed directory and bring them back over.
def checkProcessedFiles():
    processedDirName = processedDirPrefix + pathBasename(args.input)
    remoteProcessedPath = args.remote + '/' + processedDirName
    processedFiles = subprocess.check_output(['ssh', args.ssh, 'ls', remoteProcessedPath],
                                             stderr = subprocess.STDOUT).decode().splitlines()
    localProcessedDir = os.path.normpath(args.input + '/../' + processedDirName)

    try:
        os.mkdir(localProcessedDir)
    except FileExistsError as e:
        pass

    ## If files were modified, we have to sync them back over.
    if args.processedFilesModified:
        rsyncWrapper(getRsyncPath() + '/' + processedDirName + '/', localProcessedDir)

    for f in processedFiles:
        localInputFile = getCorrespondingInputFile(f)
        localInputFilePath = args.input + '/' + localInputFile
        try:
            if args.processedFilesModified:
                ## Remove input since their modified brethren are already synced
                os.remove(localInputFilePath)
            else:
                ## Otherwise, move to save sync time.
                shutil.move(localInputFilePath, localProcessedDir)
        except FileNotFoundError as e:
            pass


def getOutput():
    error = None
    currentTime = datetime.datetime.utcnow().replace(microsecond=0, tzinfo=datetime.timezone.utc).isoformat()
    localOutputPath = args.output + '/' + currentTime
    remoteOutputPath = getRsyncPath() + '/' + pathBasename(args.output) + '/'

    try:
        os.mkdir(args.output)
    except FileExistsError as e:
        pass

    rsyncWrapper(remoteOutputPath, localOutputPath)


def cleanRemoteDir():
    sshcmd = ['ssh', args.ssh, 'bash']
    heredoc = ('<< EOF\n'
               'rm -rf ' + args.remote + '/* \n'
               'EOF')
    sshcmd.append(heredoc)
    subprocess.call(sshcmd, stderr=subprocess.STDOUT)


def performWorkflow(inputFiles = []):
    ## pre execution steps
    pkgTempDir = buildPkg(args.command, inputFiles)
    cleanRemoteDir() ## clean up preexecution to ensure clean processing for each batch.
    sendPkg(pkgTempDir)
    cleanupTempPkg(pkgTempDir)

    ## execution
    successful = execRemoteCmd()

    if successful:
        ## post execution steps, only do if successful.
        if args.input:
            checkProcessedFiles()
        if args.output:
            getOutput()

    cleanRemoteDir() ## post execution cleanup regardless.


def overTime():
    if timeLimit:
        curTime = time.monotonic()
        return (curTime - startTime) > timeLimit


def setupLogging():
    global LOGGER
    commandName = pathBasename(args.command)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fileHandler = logging.handlers.TimedRotatingFileHandler("batcher.log")
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)

    LOGGER = logging.getLogger(commandName)
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.addHandler(fileHandler)


def main():
    global timeLimit
    global startTime

    setupLogging()

    startTime = time.monotonic()
    if args.timeout:
        timeLimit = float(args.timeout) * 3600

    LOGGER.info('Starting job %s with timeout %s', pathBasename(args.command), str(timeLimit))
    
    inputP = args.input
    if inputP:
        inputFiles = os.listdir(inputP)
        if args.batch:
            i = 0
            batchSize = int(args.batch)
            remainingInput = len(inputFiles)
            while batchSize < remainingInput:
                filesToSend = inputFiles[i * batchSize:(i + 1) * batchSize]
                performWorkflow(filesToSend)
                remainingInput -= batchSize
                i += 1
                if overTime():
                    return

            performWorkflow(inputFiles[-remainingInput:])
        else:
            performWorkflow(inputFiles)
    else:
        performWorkflow()


if __name__ == "__main__":
    main()
