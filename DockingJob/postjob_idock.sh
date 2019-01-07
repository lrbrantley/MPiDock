#!/bin/bash
#This script is to process results from MPiDock run with iDock
#This script assumes all ligands ran correctly.
#All results will be placed in a directory called Results
mkdir Results
cd ProcessedLigands
for f in org*.pdbqt; do grep -n "Name" $f > $f.txt; done
for f in org*.txt; do sed -i 1i"$f" $f; done
for f in org*.txt; do paste -s $f >> ZINC_IDs.txt; done
for f in org*.txt; do rm $f; done
mv ZINC_IDs.txt ../Results/
for f in ligand*pdbqt; do cut -c-66 $f > $f.pdb; done
for f in ligand*.pdb; do mv "$f" "${f%.pdbqt.pdb}_OUTPUT.pdb"; done
for f in ligand*.pdb; do mv $f ../Results/; done
cd ../Results/
for f in ligand*pdb; do sed -n '2p' $f > $f.txt; done
for f in ligand*.txt; do mv "$f" "${f%_OUTPUT.pdb.txt}.txt"; done
for f in ligand*.txt; do sed -i 1i"$f" $f; done
for f in ligand*txt; do paste -s $f >> summary.txt; done
for f in ligand*.txt; do rm $f; done
awk '{print $1" "$10}' summary.txt | sort | column -t > energy.txt
awk '{print $1" "$5}' ZINC_IDs.txt | sort | column -t > id.txt
paste energy.txt id.txt | sort -n -k2 | column -t > Summary_Final.txt
rm id.txt energy.txt