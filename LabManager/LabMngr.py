#!/bin/python3
from os import system, makedirs, chdir, path
import os
import time
import subprocess
import sys
import glob
import argparse
import re
import platform
import argparse

parser = argparse.ArgumentParser(
    prog='LABMNGR',
    description='Launch Executable across Lab 127 cluster',
    usage='%(prog)s [-options] exec')
parser.add_argument('--hostfile', action='store', default="./host_file",
                    help='Override hostfile\n(Default: ./host_file)')
parser.add_argument('executable', metavar='exec', 
                    help='the executable to run', default = "")
parser.add_argument('-n', metavar='NPM', default = 1,
                    help='Override the number of MPI nodes on each machine\n(Default: 1)')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Print verbose output')

args = parser.parse_args()

def verbose_print(*largs, **kwargs):
    if args.verbose:
        print(*largs, **kwargs)

def check_mpi():
    FNULL = open(os.devnull, 'w')
    try:
        subprocess.call(["mpic++", "-v"], stderr=FNULL)
    except OSError as e:
        print("Failed to find MPI in PATH, please add to .bashrc:")
        print("\tLD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64/openmpi/lib")
        print("\tPATH=$PATH:/usr/lib64/openmpi/bin")
        return 1
    return 0

def main():
    print ("This is a Lab 127 Impromptu Cluster Creator/Manager")
    check_mpi()
    
    #exit(1)
    
    mpi_exec = args.executable

    mpi_source = "/usr/lib64/openmpi/bin/mpiexec "
    mpi_args = "-hostfile " + args.hostfile
    mpi_args += " --mca plm_rsh_no_tree_spawn 1"
    mpi_args += " --mca btl_tcp_if_include ens6f0"
    mpi_args += " --prefix /usr/lib64/openmpi"
    mpi_args += " --map-by ppr:" + str(args.n) + ":node " 
    if args.verbose:
        mpi_args += " -display-map "

    print(mpi_source + mpi_args + mpi_exec)

    verbose_print(mpi_exec + " is running...")
    
    system(mpi_source + mpi_args + mpi_exec)

    verbose_print("Processing has finished")
    system("exit")

main()

