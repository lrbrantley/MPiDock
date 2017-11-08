#!/usr/bin/env python3
from os import system, makedirs, chdir, path
import os
import subprocess
import sys
import glob
import argparse
import re
import platform


parser = argparse.ArgumentParser(description='Launch MPI-VINA across Lab 127 cluster')
parser.add_argument('--hostfile', action='store', default="./host_file",
					help='Override default hostfile')
parser.add_argument('-v', '--verbose', action='store_true',
					help='print verbose output')
parser.add_argument('-t', '--test', action='store_true',
					help='launch test application to verify mpi connections')
parser.add_argument('-n', '--nodes', nargs='+',
					help='hardcode which nodes to run on (e.g. -n 8 9 14 3)')
parser.add_argument('-l', '--ligand', action='store', default="./Ligand",
					help="Override Ligand Directory")
parser.add_argument('-o', '--output', action='store', default="./Output",
					help="Override Output Directory")
parser.add_argument('-p', '--processed', action='store', default="./ProcessedLigand",
					help="Override Processed Ligand Directory")

args = parser.parse_args()

def verbose_print(*largs, **kwargs):
	if args.verbose:
		print(*largs, **kwargs)


def setup_script():
	user = input("What is your ssh username?: ")
	hostname = platform.node()
	verbose_print("Hostname found:" + hostname)
	ssh_path = path.expanduser("~/.ssh/")
	if not path.exists(ssh_path + "id_rsa.pub"):
		print("ERROR: public ssh key at" + "does not exist, please generate one")
		print("Run:ssh-keygen")
		exit(1)

	verbose_print("Setting up connections with Lab 127 Nodes")
	alive_nodes = list()
	# Get health of Lab 127 and find all active nodes
	for i in range(10, 37):
		# lab machines 31 and 37 don't have intel mpi installed
		if i is 31 or i is 37:
			continue
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
	i = 10
	while(i - 10 != num_nodes and i < 38):
		# lab machines 31 and 37 don't have intel mpi installed
		if i is 31 or i is 37 or i is 13:
			i = i + 1
			continue
		cmd = "127x" + str(i) + ".csc.calpoly.edu"
		val = 0
		try:
			val = subprocess.check_output(['ping', '-c 1', cmd])
		except subprocess.CalledProcessError as e:
			i = i + 1
			continue
		if val is not 0:
			good_nodes.append(cmd)
		i = i + 1
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

def preprocess_ligands():
	verbose_print("Preprocess " + args.ligand)
	system("./preprocess.bash " + args.ligand)
	system("ls > ligandlist " + args.ligand)

	makedirs(name=args.output, exist_ok=True)
	makedirs(name=args.processed, exist_ok=True)

def postprocess_ligands():
	#Result analysis.
	print("Analysizing the results...")

	chdir("./Output")
	
	for file in glob.glob('*.pdbqt'):
		cmd = "cut -c-66 "+file+" > "+path.basename(file).split('.')[0]+"_OUTPUT.pdb"
		system(cmd)

	zincId = ""
	topRes = ""
	for file in glob.glob('inh*.txt'):
		ligandName = path.basename(file).split('.')[0]
		with open(file) as ligandTxt:
			for i,line in enumerate(ligandTxt):
				if i == 25:
					topRes = line.split()[1]
					break
		with open(ligandName+"_OUTPUT.pdb") as ligandData:
			for line in ligandData:
				res = re.findall(r'Name', line)
				if res:
					zincId = line.split()[3]
					break

		with open('summary.txt', 'a+') as summary:
			summary.write(ligandName+".pdbqt\t"+topRes+"\t"+zincId+'\n')
		os.replace(file, ligandName + '.txt')
				


	print("See the 'summary.txt' file in the", "'" +args.output+"' directory.")
	print("Sorting the results...")
	system("sort -n -k 2 summary.txt -o Summary_Final.txt")
	print("See the 'Summary_Final.txt' file in the", "'"+args.output+"' directory.")


def main():
	print ("This is a Lab 127 Impromptu Cluster Creator/Manager")
	inital = '~'
	while( inital is not 'y' and inital is not 'n'):
		inital = input("Is this the first time running this script on this machine (y/n)?: ")
	if inital is 'y':
		setup_script()

	if args.nodes:
		alive = hardcode_lab_state(args.nodes)
	else:
		num_nodes = 0
		while( num_nodes < 1 or num_nodes > 26 ):
			inputs = input ("Enter the number of machines you wish to use (1 to 26): ")
			num_nodes = int(inputs)

		
		alive = rewrite_lab_state(num_nodes)
	
	print("Using Nodes:");
	for n in alive:	print(n)

	preprocess_ligands()

	mpi_exec = " mpiVINAv3"
	system("make" + mpi_exec)

	mpi_source = "mpiexec "
	mpi_args = ""
	mpi_args = "--mca plm_rsh_no_tree_spawn 1"
	#mpi_args += " --mca btl_base_verbose 30"
	mpi_args += " --prefix /usr/lib64/openmpi/"
	mpi_args += " --map-by ppr:2:node" 
	#mpi_args += " -display-map"
	mpi_args += " -hostfile " + args.hostfile
	exec_args = " " + args.ligand + " " + args.output + " " + args.processed
	if args.test:
		mpi_out = " mpi_hello_world"
	else:
		if args.verbose:
			mpi_out = mpi_exec + exec_args + " | tee " + args.output + "/MpiVina.log"
		else:
			mpi_out = mpi_exec + exec_args + " > " + args.output + "/MpiVina.log"

	print(mpi_source + mpi_args + mpi_out)

	print("MPI-Vina is running...")
	
	system(mpi_source + mpi_args + mpi_out)

	print("Processing has finished")
	print("See the MpiVina.log file.")

	postprocess_ligands()
	

main()
