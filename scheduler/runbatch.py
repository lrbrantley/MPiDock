#!/usr/bin/env python3
import argparse
import datetime
import os
import shutil
import subprocess
import tempfile
import time

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
            shutil.copy2(fileP, tempDir + '/' + inputDirName)
        os.mkdir(tempDir + '/' + processedDirPrefix + inputDirName)

    if args.output:
        os.mkdir(tempDir + '/' + pathBasename(args.output))
    
    if args.miscdir:
        shutil.copytree(args.miscdir, tempDir + '/' + pathBasename(args.miscdir))
        
    return tempDir


## attempts to sync package over remotely. If it fails 5 attempts, throws the most recent error.
def sendPkg(tempDir):
    error = None
    for i in range(5):
        try:
            ## If you append a '/' at the end of a directory, rsync will transfer everything inside of it and not
            ## send the directory itself, which is more what we want.
            subprocess.check_output(['rsync','-avz', tempDir + '/', getRsyncPath()], stderr=subprocess.STDOUT)
            return
        except subprocess.CalledProcessError as e:
            error = e
    raise error


def cleanupTempPkg(tempDir):
    shutil.rmtree(tempDir)


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
    subprocess.call(sshcmd, stderr=subprocess.STDOUT)


## If there's a prefix, remove it to figure out the input file.
def getCorrespondingInputFile(processedFile):
    prefix = args.processedPrefix
    if prefix is not None and processedFile.startswith(prefix):
        return processedFile[len(prefix):]
    else:
        return processedFile


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
        subprocess.check_output(['rsync', '-avz', getRsyncPath() + '/' + processedDirName + '/', localProcessedDir], stderr=subprocess.STDOUT)

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
    for i in range(5):
        try:
            subprocess.check_output(['rsync', '-avz', remoteOutputPath, localOutputPath], stderr=subprocess.STDOUT)
            return
        except subprocess.CalledProcessError as e:
            error = e
    raise error


## package cleanup only removes input, output, and processed directories. This saves on sync time for command and miscdir.
def cleanupPkg():
    inputDir = pathBasename(args.input)
    processedDir = processedDirPrefix + inputDir
    outputDir = pathBasename(args.output)
    sshcmd = ['ssh', args.ssh, 'bash']
    heredoc = ('<< EOF\n'
               'cd ' + args.remote + '\n'
               'rm -rf ' + inputDir + ' ' + processedDir + ' ' + outputDir + '\n'
               'EOF')
    sshcmd.append(heredoc)
    subprocess.call(sshcmd, stderr=subprocess.STDOUT)


def performWorkflow(inputFiles = []):
    ## pre execution steps
    pkgTempDir = buildPkg(args.command, inputFiles)
    sendPkg(pkgTempDir)
    cleanupTempPkg(pkgTempDir)

    ## execution
    execRemoteCmd()

    ## post execution steps
    if args.input:
        checkProcessedFiles()
    if args.output:
        getOutput()
    cleanupPkg()


def overTime():
    if timeLimit:
        curTime = time.monotonic()
        return (curTime - startTime) > timeLimit


def main():
    global timeLimit
    global startTime

    if args.timeout:
        timeLimit = float(args.timeout) * 3600
        startTime = time.monotonic()
    
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