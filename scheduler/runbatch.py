#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import tempfile
import time

processedDirName = 'ProcessedInput'
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
parser.add_argument('-to', '--timeout',
        help='Time limit for batches to run. After time limit is reached no further batches will be sent.')
parser.add_argument('-args', '--arguments',
        help='Arguments to send to remote command')
parser.add_argument('-mdir', '--miscdir', help='Location of extra directory to send over. Will be in \"miscdir\" of package')

def rsyncPath():
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
        os.mkdir(tempDir + '/' + processedDirName)

    if args.output:
        os.mkdir(tempDir + '/output')
    
    if args.miscdir:
        shutil.copytree(args.miscdir, tempDir + '/miscdir')
        
    return tempDir


## attempts to sync package over remotely. If it fails 5 attempts, throws the most recent error.
def sendPkg(tempDir):
    error = None
    for i in range(5):
        try:
            subprocess.check_output(['rsync','-avz', tempDir, rsyncPath], stderr=subprocess.STDOUT)
            return
        except subprocess.CalledProcessError as e:
            error = e
    raise error


def cleanupTempPkg(tempDir):
    shutil.rmtree(tempDir)


def execRemoteCmd():
    sshcmd = ['ssh', args.ssh]
    heredoc = ('<< EOF\n'
               'cd ' + args.remote + '\n'
               './' + pathBasename(args.command) + ' ' + args.arguments + '\n'
               'EOF')
    sshcmd.append(heredoc)
    subprocess.call(sshcmd, stderr=subprocess.STDOUT)


def checkProcessedFiles():
    remoteProcessedPath = '\'' + args.remote + '/' + processedDirName + '\''
    processedFiles = subprocess.check_output(['ssh', args.ssh, 'ls', remoteProcessedPath],
                                             stderr = subprocess.STDOUT).splitlines()
    localProcessedDir = os.path.normpath(args.input + '../' + processedDirName)
    try:
        os.mkdir(localProcessedDir)
    except FileExistsError as e:
        ## do nothing.
        
    for f in processedFiles:
        shutil.move(args.input + '/' + f, localProcessedDir)


def getOutput():
    error = None
    for i in range(5):
        try:
            subprocess.check_call(['rsync', '-avz', args.remote + '/output', args.output],
                                  stderr = subprocess.STDOUT)
            return
        except subprocess.CalledProcessError as e:
            error = e
    raise error


## package cleanup only removes input, output, and processed directories. This saves on sync time for command and miscdir.
def cleanupPkg():
    sshcmd = ['ssh', args.ssh]
    heredoc = ('<< EOF\n'
               'cd ' + args.remote + '\n'
               'rm -rf ' + pathBasename(args.input) + ' output ' + processedDirName + '\n'
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

def overTime(startTime):
    if timeLimit:
        curTime = time.monotonic()
        return (curTime - startTime) > timeLimit


def main():
    args = parser.parse_args()
    command = args.command

    startTime = None
    if args.timeout:
        timeLimit = int(args.timeout)
        startTime = time.monotonic()
    
    inputP = args.input
    if inputP:
        inputFiles = os.listdir(inputP)
        if args.batch:
            i = 0
            batchSize = int(args.batch)
            remainingInput = len(inputFiles)
            while batchSize < remainingInput:
                filesToSend = inputFiles[i * batchSize, (i + 1) * batchSize]
                performWorkflow(filesToSend)
                remainingInput -= batchSize
                i += 1
                if overTime(startTime):
                    return

            performWorkflow(inputFiles[-remainingInput:])
        else:
            performWorkflow(inputFiles)
    else:
        performWorkflow()


if __name__ == "__main__":
    main()
