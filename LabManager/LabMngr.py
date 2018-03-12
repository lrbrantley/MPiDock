#!/usr/bin/env python3
from os import system, makedirs, chdir, path
import os
import time
import subprocess
import sys
import glob
import argparse
import re
import platform


parser = argparse.ArgumentParser(
    prog='LABMNGR',
    description='Launch mpiDock across the MPAC Lab cluster',
    usage='%(prog)s [options]')
parser.add_argument('-l', '--ligand', action='store', default="./Ligand",
                    help="Override Ligand Folder")
parser.add_argument('-o', '--output', action='store', default="./Output",
                    help="Override Output Folder")
parser.add_argument('-p', '--processed', action='store', default="./ProcessedLigand",
                    help="Override Processed Folder")
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Print verbose output')
parser.add_argument('-s', '--setup',action='store_true',
                    help="Run first-time setup script")
parser.add_argument('-n', '--nodes', nargs='+',
                    help='Hardcode which nodes to run on (e.g. -n 08 09 14 03)')
parser.add_argument('-x', '--exclude', nargs='+', type=int, default=list(),
                    help='Exclude nodes from program (e.g. -x 31 02 15)')
parser.add_argument('--Vina', action='store_true',
                    help="Run MPIVina instead of MPiDock")
parser.add_argument('--hostfile', action='store', default="./src/hostFile",
                    help='Override default hostfile')
parser.add_argument('-t', '--timeout', action='store', default='-1',
                    help='Seconds MPiDock will run before exiting')
parser.add_argument('-r', '--ratio', action='store', default="2",
                    help="Division of Block size ratio (Default is 2)")
parser.add_argument('--wpm', action='store', default="4",
                    help="Workers Per Machine (Default is 4)")


args = parser.parse_args()

def verbose_print(*largs, **kwargs):
    if args.verbose:
        print(*largs, **kwargs)

# Login to all machines possible and setup ssh passwordless
def setup_script():
    user = input("What is your ssh username?: ")
    hostname = platform.node()
    verbose_print("Hostname found:" + hostname)
    ssh_path = path.expanduser("~/.ssh/")
    if not path.exists(ssh_path + "id_rsa.pub"):
        print("ERROR: public ssh key at" + "does not exist, please generate one")
        print("Run:ssh-keygen")
        exit(1)

    verbose_print("Setting up connections with MPAC Lab Nodes")
    alive_nodes = list()
    # Get health of MPAC Lab and find all active nodes
    for i in range(1, 37):
        if i < 10:
            cmd = "127x0" + str(i) + ".csc.calpoly.edu"
        else:
            cmd = "127x" + str(i) + ".csc.calpoly.edu"
        val = 0
        try:
            val = subprocess.check_output(['ping', '-c 1', cmd])
        except subprocess.CalledProcessError as e:
            continue
        if val is not 0:
            alive_nodes.append(cmd)

    # add nodes to known_hosts file
    for node in alive_nodes:
        system("ssh-keygen -R " + node)
        system("ssh-keyscan -H " + node + " >> ~/.ssh/known_hosts")
        system("ssh-keyscan -H " + hostname + " >> ~/.ssh/known_hosts")
        # setup public ssh key login
        system("ssh-copy-id -i ~/.ssh/id_rsa.pub " + user + "@" + node)

    verbose_print("Successful setup ssh keys with:")
    for node in alive_nodes: verbose_print(node)


    verbose_print("Setup Complete")

# For the -n flag, check if the nodes are valid and create hostFile
def hardcode_lab_state(nodes):
    good_nodes = list()
    for n in nodes:
        cmd = "127x" + str(n) + ".csc.calpoly.edu"
        val = 0
        try:
            val = subprocess.check_output(['ping', '-c 1', cmd])
        except subprocess.CalledProcessError as e:
            continue
        if val is not 0:
            good_nodes.append(cmd)
 
    #Ensure that current machine is top of the list
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
    

def rewrite_lab_state(num_nodes):
    good_nodes = list()
    i = 1
    while(i - 1 != num_nodes and i < 38):
        # Exclude machine 2 and 36 because passwordless ssh doesn't work them
        if i is 2 or i is 36 or i in args.exclude:
            i = i + 1
            continue
        if i < 10:
            cmd = "127x0" + str(i) + ".csc.calpoly.edu"
        else:
            cmd = "127x" + str(i) + ".csc.calpoly.edu"
        val = 0
        try:
            val = subprocess.check_output(['ping', '-c 1', cmd])
        except subprocess.CalledProcessError as e:
            i = i + 1
            continue
        # Ping call was successful, machine is reachable
        if val is not 0:
            good_nodes.append(cmd)
        i = i + 1
    
    # Ensure that current machine is in the list
    # and force it to the top of the list
    hoster = subprocess.check_output(['hostname'])
    hoster = str(hoster, 'utf-8')
    hoster = hoster.rstrip('\n')
    if hoster in good_nodes:
        good_nodes.remove(hoster)
    good_nodes.insert(0, hoster)

    # Populate hostFile with active machines
    with open(args.hostfile, 'w') as hosts:
        for node in good_nodes:
            hosts.write(node + " slots=" + args.wpm + '\n')
    return good_nodes

# Launch preprocess bash script
def preprocess_ligands():
    verbose_print("Preprocess " + args.ligand)
    system("./src/preprocessVina.bash " + args.ligand)

# Generates ligandList file and ensures that
# Output and Processed folders exist
def prepare_run():
    system("ls > ligandList " + args.ligand)

    makedirs(name=args.output, exist_ok=True)
    makedirs(name=args.processed, exist_ok=True)

def postprocess_ligands():
    if args.Vina:
        post_bash = './src/postprocessVina.bash '
    else:
        post_bash = './src/postprocessiDock.bash '
    cmd = post_bash + args.output + " " + args.processed
    verbose_print(cmd)
    system(cmd)

# Checks for the existence of the mpiexec and the correct version
# in order to verify that mpi exists on the main node
def check_mpi():
    verbose_print("Checking if MPI exists in PATH")
    FNULL = open(os.devnull, 'w')
    result = ""
    try:
        result = subprocess.check_output(["mpiexec", "--version"], stderr=FNULL)
    except OSError as e:
        print("ERROR: Failed to find MPI in PATH, please add to .bashrc:")
        print("\tLD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64/openmpi/lib")
        print("\tPATH=$PATH:/usr/lib64/openmpi/bin")
        print("\texport LD_LIBRARY_PATH")
        print("\texport PATH")
        return 1
    result = result.decode()
    result = result.split('\n')[0]
    result = result.split(' ')[2]
    major_ver = result.split('.')[0]
    minor_ver = result.split('.')[1]
    if major_ver is not '1':
    	print('WARNING: Incorrect version of MPI identified')
    	print('Version 1.10 is supported, identified version ' + result)
    	return 1
    return 0

def main():
    print ("MPAC Lab Impromptu Cluster Creator/Manager")
    if check_mpi() == 1:
    	exit(1)
    if args.setup:
        setup_script()
        exit(0)

    if args.nodes:
        alive = hardcode_lab_state(args.nodes)
    else:
        num_nodes = 0
        while( num_nodes < 1 ):
            inputs = input ("Enter the number of machines you wish to use (1 to 35): ")
            num_nodes = int(inputs)
        alive = rewrite_lab_state(num_nodes)
    
    print("Using " + str(len(alive)) + " Nodes:");
    verbose_print(alive)

    if args.Vina:
        preprocess_ligands()

    prepare_run()

    if args.timeout != "-1":
        os.environ['MPIEXEC_TIMEOUT'] = args.timeout

    #Generate MPiDock or MPIVina from source files
    if args.Vina:
        mpi_exec = " MPIVina"
        args.wpm = '2'
        exec_log = '/MPIVina.log'
    else:
        mpi_exec = " MPiDock"
        exec_log = '/MPiDock.log'

    system("make -C ./src" + mpi_exec)

    mpi_source = "mpiexec "
    # Use the ssh information for the current machine in a spider pattern
    # without this mpi attempts to ssh in a ring patter from worker to worker
    mpi_args = "--mca plm_rsh_no_tree_spawn 1"
    # Use the eno1 network connection, this is the required network interface 
    # for the MPAC lab
    mpi_args += " --mca btl_tcp_if_include eno1"
    mpi_args += " --prefix /usr/lib64/openmpi/"
    # Enable 2 workers per machine for a total of 12 cores per machine
    mpi_args += " --map-by ppr:" + args.wpm + ":node" 
    # Displays verbose information about the cluster
    #mpi_args += " -display-map"
    # Use the created hostFile for the ssh information
    mpi_args += " -hostfile " + args.hostfile
    exec_args = " " + args.ligand + " " + args.output + " " + args.processed 
    exec_args += " " + args.ratio 
    
    if args.verbose:
        mpi_out = mpi_exec + exec_args + " | tee " + args.output + exec_log
    else:
        mpi_out = mpi_exec + exec_args + " > " + args.output + exec_log

    verbose_print(mpi_source + mpi_args + mpi_out)

    print("MPI is running...")
    
    subprocess.call(mpi_source + mpi_args + mpi_out, shell=True)
    
    # Clear any timeouts for mpi if they exist
    system('unset MPIEXEC_TIMEOUT')

    print("Processing has finished")
    
    print("Beginning PostProcessing")
    postprocess_ligands()
    print("See the "+ exec_log +" file in the "+ args.output +" directory.")

    

main()
