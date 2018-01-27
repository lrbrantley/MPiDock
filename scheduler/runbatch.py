#!/usr/bin/env python3
from os import listdir
import argparse

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

def scpPath():
    return args.ssh + ':' + args.remote-path

def main():
    args = parser.parse_args()
    command = args.command
    
    inputP = args.input
    if inputP is not None:
        inputFiles = listdir(inputP)




if __name__ == "__main__":
    main()
