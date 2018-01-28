#!/usr/bin/env python3
import argparse
import os
import shutil
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('command', help='Location of Command to execute remotely')
parser.add_argument('ssh', help='User and Remote SSH Address or an alias')
parser.add_argument('remote-path', help='Location on remote machine')
parser.add_argument('-i', '--input',
        help='Location for input files. These will be transfered')
parser.add_argument('-o', '--output',
        help='Location for output files. Remote output will be transfered back into this folder')
parser.add_argument('-b', '--batch',
        help='Number of input files to transfer per usage. Defaults to all of them')
parser.add_argument('-to', '--timeout',
        help='Time limit for this job (and the remote job) to run. If the batch setting is\
                used as well, batches will be run until time runs out.')
parser.add_argument('-args', '--arguments',
        help='Arguments to send to remote command')
parser.add_argument('-mdir', '--miscdir', help='Location of extra directory to send over')

def rsyncPath():
    return args.ssh + ':' + args.remote-path

def pathBasename(p):
    return os.path.basename(os.path.normpath(p))

## buildPkg makes a temporary directory with files to be sent. Returns absolute path of temp dir.
def buildPkg(cmdPath, inputFiles = []):
    tempDir = tempfile.mkdtemp()
    shutil.copy2(cmdPath, tempDir)

    if args.input:
        inputDirName = pathBasename(args.input)
        os.mkdir(tempDir + "/" + inputDirName)
        for inF in inputFiles:
            fileP = args.input + "/" + inF
            shutil.copy2(fileP, tempDir + "/" + inputDirName)
        os.mkdir(tempDir + "/processedInput")

    if args.output:
        os.mkdir(tempDir + "/output")
    
    if args.miscdir:
        shutil.copytree(args.miscdir, tempDir)
        
    return tempDir

def sendPkg(tempDir):



def main():
    args = parser.parse_args()
    command = args.command
    
    inputP = args.input
    if inputP:
        inputFiles = os.listdir(inputP)
        if args.batch:
            i = 0
            batchSize = int(args.batch)
            remainingInput = len(inputFiles)
            while batchSize < remainingInput:
                filesToSend = inputFiles[i * batchSize, (i + 1) * batchSize]
                i += 1
                ##build package
                ##sync
                ##exec command
                ##retrieve processed inputs
                ##move processed inputs to processed folder locally (../processed relative to input path).









if __name__ == "__main__":
    main()
