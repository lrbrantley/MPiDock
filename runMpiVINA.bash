#!/bin/bash
#
#SBATCH -N 1
#SBATCH -n 8
#SBATCH -c 6
#SBATCH -t 3-00:00:00
#SBATCH -o testrun.out
#SBATCH -e testrun.err

#Compile the application.
ls ./Ligand > ligandlist
mkdir -p Output
mkdir -p ProcessedLigand
make

#Run the application.
echo "MPI-Vina is running..."
mpirun mpiVINA
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
