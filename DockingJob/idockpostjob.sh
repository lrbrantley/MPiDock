#!/bin/bash
#this script is to process results from MPiDock
#the ZINC_org.txt file is for the MPi_fix script
cd ProcessedLigands
for f in org*.pdbqt; do grep -n "Name" $f > $f.txt; done
for f in org*.txt; do sed -i 1i"$f" $f; done
for f in org*.txt; do paste -s $f >> ZINC_org.txt; done
mv ZINC_org.txt ../
for f in org*; do rm $f; done
for f in *.pdbqt; do cut -c-66 $f > $f.pdb; done
for f in *.pdb; do mv "$f" "${f%.pdbqt.pdb}_OUTPUT.pdb"; done
for f in ligand*.pdbqt; do rm $f; done
cd ../Output/
cat */Summary_Final.txt > SuperSummary.txt
column -t SuperSummary.txt > Column.txt
sort -k2 -n Column.txt -o Summary_Final.txt
mv Summary_Final.txt ../
cd ../
rm -rf Output
cp Summary_Final.txt ProcessedLigands/
mv ProcessedLigands Results
cd ../
rm batcher.log*
#result

#This script will try to fix a MPi run with missing values in the summary file
#Execute this script in the parent of the Results directory.  There should also
#be a file called ZINC_org.txt from the cleanup script.
cp ZINC_org.txt Results/
cd Results/
for f in ligand*.pdb; do grep "NORMALIZED" $f > $f.txt; done
for f in ligand*.txt; do mv "$f" "${f%.pdb.txt}.txt"; done
for f in ligand*.txt; do sed -i 1i"$f" $f; done
for f in ligand*.txt; do sed -n '1p;2p' $f > Best_$f; done
for f in ligand*.txt; do rm $f; done
for f in Best*.txt; do paste -s $f >> Summary_Fix.txt; done
sed -e 's/org_//g' -e 's/.pdbqt.txt//g' ZINC_org.txt > id1.txt
awk '{print $1" "$5}' id1.txt | column -t >> id2.txt
awk '{print $1" "$10}' Summary_Fix.txt | column -t >> energy.txt
sed -e 's/_OUTPUT.txt//g' energy.txt > energy2.txt
awk '{print $1}' id2.txt | sed '/^$/d' | sort -n > id3.txt
awk '{print $1}' energy2.txt | sed '/^$/d' | sort -n > energy3.txt
comm -12 id3.txt energy3.txt | awk 'NF' > match.txt
awk 'NR==FNR { A[$1]=1; next }; A[$1]' match.txt id2.txt > clean_id.txt
awk 'NR==FNR { A[$1]=1; next }; A[$1]' match.txt energy2.txt > clean_energy.txt
paste clean_energy.txt clean_id.txt > final.txt
sort -n -k2 final.txt > final2.txt
column -t final2.txt > Summary_Final_Fix.txt
rm clean*.txt energy*.txt final*.txt id*.txt match.txt
cp Summary_Final_Fix.txt ../
#result
