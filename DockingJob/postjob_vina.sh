#!/bin/bash
#This script is to process results from MPiDock run with Vina
#and should be executed from the DockingJobs directory.
#All results will be placed in a directory called Results
#Note that if you try to cat all Summary files from the output folders, the text
#files may be missing some values, even though the pdb output file exists.
#Best to get the result energy values from the pdb files in the Results directory
mkdir Results
cd ProcessedLigands
for f in inh*.pdbqt; do grep -n "Name" $f > $f.txt; done
for f in inh*.txt; do sed -i 1i"$f" $f; done
for f in inh*.txt; do paste -s $f >> ZINC_IDs.txt; done
for f in inh*.txt; do rm $f; done
mv ZINC_IDs.txt ../Results/
cd ../Output
for f in */*.pdb; do cp $f ../Results/; done
cd ../Results/
for f in inh*pdb; do sed -n '2p;3p' $f > $f.txt; done
for f in inh*.txt; do mv "$f" "${f%_OUTPUT.pdb.txt}.txt"; done
for f in inh*.txt; do sed -i 1i"$f" $f; done
for f in inh*txt; do paste -s $f >> summary.txt; done
for f in inh*.txt; do rm $f; done
awk '{print $1" "$5}' summary.txt | sort | column -t > energy.txt
awk '{print $1" "$5}' ZINC_IDs.txt | sort | column -t > id.txt
paste energy.txt id.txt | sort -n -k2 | column -t > Summary_Final.txt
rm id.txt energy.txt