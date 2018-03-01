#!/bin/bash
#
#SBATCH -N 1
#SBATCH -n 4
#SBATCH -c 6
#SBATCH -t 3-00:00:00
#SBATCH -o testrun.out
#SBATCH -e testrun.err

cleanInputFile ()
{
   local FILE=$1;
   local ZINCID=$(grep "ZINC" $FILE |   # Move ZINC Ids to a REMARK, not USER, line.
                  sed 's/USER/REMARK/');
   sed -i -e "1i $ZINCID" -e '/USER/d' -e '/TER/d' $FILE;
}

#Copy over and Ensure all inh_ files don't have unusable things.
cd Ligand
for f in ligand*.pdbqt; do # Move files in parallel.
   mv $f inh_$f &
done
wait # Join sub processes.
for f in inh*.pdbqt; do    # Edit files in parallel.
   cleanInputFile $f &
done
wait # Join sub processes.
cd ..

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
for f in *.pdbqt; do
   cut -c-66 "$f" > "${f%.pdbqt}_OUTPUT.pdb"; # cut first 66 chars and write to file.
done
for f in inh*.txt; do
   ligand=$(basename $f .txt);                   # inhibitor ligand name from file.
   topRes=$(sed -n '25p' $f |                    # grab top result row from log file.
            awk '{print $2}');                   # extract energy value from row.
   zincId=$(grep "Name" "${ligand%.pdbqt}_OUTPUT.pdb" | # grab Zinc Name row(s) from output file.
            head -1 |                            # reduce to single row
            awk '{print $4}');        	         # get ZINC name.
   echo -e "$ligand\t$topRes\t$zincId" >> summary.txt;  # Output to summary file.
   mv "$f" "${f%.pdbqt.txt}.txt";       # Change log files to *.txt files.
done
echo "See the 'summary.txt' file in the 'Output' directory."

echo "Sorting the results..."
sort -n -k 2 summary.txt -o Summary_Final.txt # Sort by binding energy
echo "See the 'SortedResult' file in the 'Output' directory."
#cat SortedResult
