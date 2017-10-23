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
for f in inh*.txt; do
   ligand='basename $f .txt';         # inhibitor ligand name from file.
   topRes='sed -n '25p' $f';          # grab top result from log file.
   zincId=$(grep "Name" $ligand.pdb | # grab Zinc Name row(s) from output file.
            head -1 |                 # reduce to single row
            awk '{print $4}');        # get ZINC name.
   echo "$ligand\t$topRes\t$zincId" >> summary.txt;  # Output to summary file.
done
echo "See the 'summary.txt' file in the 'Output' directory."

echo "Sorting the results..."
sort -n -k 3 summary.txt -o Summary_Final.txt # Sort by binding energy
echo "See the 'SortedResult' file in the 'Output' directory."
#cat SortedResult
