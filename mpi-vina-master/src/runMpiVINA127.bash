#!/bin/bash
#This is the script for running the application by providing -np parameter from terminal.

#Compile the application.
ls > ligandlist ./Ligand
mkdir -p Output
mkdir -p ProcessedLigand
make

STATE="plm_rsh_no_tree_spawn 1"
HOST=host_file
#Run the application.
echo "MPI-Vina is running..."
/usr/lib64/openmpi/bin/mpirun --mca ${STATE} -hostfile $HOST -np 4 mpiVINA > Output/MpiVina.log
echo "Processing has finished"
echo "See the MpiVina.log file."

#Result analysis.
echo "Analysizing the results..."
cd Output
grep "  1 " *.txt | cut -c1-12,35-42 > result 
#grep "  1 " *.txt | cut -c1-7,30-35 > result
echo "See the 'result' file in the 'Output' directory."
#cat result

echo "Sorting the results..."
sort -n +1 -2 result -o SortedResult
echo "See the 'SortedResult' file in the 'Output' directory."
#cat SortedResult
