#!/bin/python3
from os import system, makedirs, chdir
import subprocess
import sys
import argparse
import platform

parser = argparse.ArgumentParser(description='Launch MPI-VINA across Lab 127 cluster')
parser.add_argument('-r', '--reset', action='store_true',  default=False,
                    help='rewrite host_file with currently active nodes')
parser.add_argument('--hostfile', action='store', default="./host_file",
                    help='change which hostfile is used')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='print verbose output')
parser.add_argument('-t', '--test', action='store_true',
                    help='launch test application to verify mpi connections')
args = parser.parse_args()

def verbose_print(string):
    if args.verbose:
        print(string)


def setup_script():
	user = input("What is your ssh username?: ")
	hostname = platform.node()
	verbose_print("Hostname found:" + hostname)
	verbose_print("Setting up connections with Lab 127 Nodes")
	alive_nodes = list()
	for i in range(10, 37):
		cmd = "127x" + str(i) + ".csc.calpoly.edu"
        val = 0
        try:
            val = subprocess.check_output(['ping', '-c 1', cmd])
        except subprocess.CalledProcessError as e:
            continue
        if val is not 0:
        	alive_nodes.append(cmd)

    for node in alive_nodes:
    	system("ssh-keygen -R " + hostname)
    	system("ssh-keygen -R " + node)
    	system("ssh-keygen -H " + node + " >> ~/.ssh/known_hosts")
    	system("ssh-keygen -H " + hostname + " >> ~/.ssh/known_hosts")
    verbose_print("Successful setup ssh keys with:")
    for node in alive_nodes: verbose_print(node)


	verbose_print("Setup Complete")


def rewrite_lab_state(num_nodes):
    good_nodes = list()
    for i in range(10, 9 + num_nodes):
        cmd = "127x" + str(i) + ".csc.calpoly.edu"
        val = 0
        try:
            val = subprocess.check_output(['ping', '-c 2', cmd])
        except subprocess.CalledProcessError as e:
            continue
        if val is not 0:
            good_nodes.append(cmd)
    hoster = subprocess.check_output(['hostname'])
    hoster = str(hoster, 'utf-8')
    hoster = hoster.rstrip('\n')
    if hoster in good_nodes:
        good_nodes.remove(hoster)
    good_nodes.insert(0, hoster)

    with open(args.hostfile, 'w') as hosts:
        for node in good_nodes:
            hosts.write(node + " slots=2" + '\n')
    return good_nodes

def main():
    print ("This is a Lab 127 Impromptu Cluster Creator/Manager")
    inital = '~'
    while( inital is not 'y' and inital is not 'n'):
    	inital = input("Is this the first time running this script on this machine (y/n)?: ")
    if inital is 'y':
    	setup_script()

    num_nodes = 0
    while( num_nodes < 1 or num_nodes > 26 ):
        inputs = input ("Enter the number of machines you wish to use (1 to 26): ")
        num_nodes = int(inputs)

    if args.reset:
        alive = rewrite_lab_state(num_nodes)
        print("Using Nodes:");
        for n in alive:
            print(n)

    system("ls > ligandlist ./Ligand")

    makedirs(name="./Output", exist_ok=True)
    makedirs(name="./ProcessedLigand", exist_ok=True)

    system("make")

    mpi_source = "/usr/lib64/openmpi/bin/mpirun "
    mpi_args = "--mca plm_rsh_no_tree_spawn 1"
    mpi_args += " -np " + str(num_nodes)
    mpi_args += " --map-by node "
    mpi_args += " -hostfile " + args.hostfile
    if args.test:
    	mpi_out = " mpi_hello_world"
    else:
    	if args.verbose:
    		mpi_out = " mpiVINA | tee Output/MpiVina.log"
    	else:
    		mpi_out = " mpiVINA > Output/MpiVina.log"

    verbose_print(mpi_source + mpi_args + mpi_out)

    print("MPI-Vina is running...")
    
    system(mpi_source + mpi_args + mpi_out)

    print("Processing has finished")
    print("See the MpiVina.log file.")

    #Result analysis.
    print("Analysizing the results...")

    chdir("Output")
    system("grep \"  1 \" *.txt | cut -c1-12,35-42 > result ")

    print("See the 'result' file in the 'Output' directory.")
    print("Sorting the results...")
    system("sort -n +1 -2 result -o SortedResult")
    print("See the 'SortedResult' file in the 'Output' directory.")

main()
