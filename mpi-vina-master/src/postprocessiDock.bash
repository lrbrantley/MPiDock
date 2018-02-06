#!/bin/bash

grabZincId()
{
   local MYFILE=$1;
   local name=${MYFILE#org_} ## Strip off org_ prefix of processed files.
   local zincId=$(grep "Name" $1 | uniq | awk '{print $4}');
   echo -e "$name\t$zincId" >> zincs.txt;
}

grabOutputData()
{
   local MYFILE=$1;
   local nameAndTopRes=$(sed -n '10p' $MYFILE |                      # grab top result row from log file.
                         awk '{print $2"\t"$4}');                          # extract energy value from row.
   echo -e "$nameAndTopRes" >> summary.txt;        # Output to summary file.
   mv "$MYFILE" "${MYFILE%.pdbqt.txt}.txt";                   # Change log files to *.txt files.
}

## Change to Processed folder to grab zinc ids from original processed files.
cd $2
for f in org_*; do
   grabZincId $f &
done
wait
mv zincs.txt ../$1

cd ..

echo "Analysizing the results..."
cd $1
for f in inh*.txt; do
   grabOutputData $f &
done
wait

## Associate energy to ZINCID by Ligand Names.
sort zincs.txt -o zincs.txt
sort summary.txt -o summary.txt
paste summary.txt zincs.txt > Summary_Final.txt

echo "Sorting the results..."
sort -n -k2 Summary_Final.txt -o Summary_Final.txt

echo "See the 'SortedResult' file in the 'Output' directory."
