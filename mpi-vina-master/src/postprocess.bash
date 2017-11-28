#!/bin/bash

grabOutputData()
{
   local MYFILE=$1;
   local ligand=$(basename $MYFILE .txt);                     # inhibitor ligand name from file.
   local topRes=$(sed -n '25p' $MYFILE |                      # grab top result row from log file.
                  awk '{print $2}');                          # extract energy value from row.
   local zincId=$(grep "Name" "${ligand%.pdbqt}_OUTPUT.pdb" | # grab Zinc Name row(s) from output file.
                  head -1 |                                   # reduce to single row
                  awk '{print $4}');        	                 # get ZINC name.
   echo -e "$ligand\t$topRes\t$zincId" >> summary.txt;        # Output to summary file.
   mv "$MYFILE" "${MYFILE%.pdbqt.txt}.txt";                   # Change log files to *.txt files.
}

echo "Analysizing the results..."
cd $1
for f in *.pdbqt; do
   cut -c-66 "$f" > "${f%.pdbqt}_OUTPUT.pdb" & # cut first 66 chars and write to file.
done
for f in inh*.txt; do
   grabOutputData $f &
done
echo "See the 'summary.txt' file in the 'Output' directory."

echo "Sorting the results..."
sort -n -k 2 summary.txt -o Summary_Final.txt # Sort by binding energy
echo "See the 'SortedResult' file in the 'Output' directory."

