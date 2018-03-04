#!/bin/bash

## This makes it so that empty wildcard expansions are null rather than literals.
shopt -s nullglob

OUTPUT_DIR=$1
PROCESSED_DIR=$2

grabZincId()
{
   local MYFILE=$1;
   local name=${MYFILE#org_} ## Strip off org_ prefix of processed files.
   local zincId=$(grep "Name" $1 | uniq | awk '{print $4}');
   echo -e "$name\t$zincId" >> zincs.txt;
}

## iDock instances killed early still output some bad data, this gets
## rid of those files so that they don't screw up the summary.
## ASSUMES you're in the output directory!!!!
ensureValidOutputAndProcess()
{
   local MYFILE=$1;
   local EXPECTED_PROCESSED_FILE=org_${f%.txt};
   ## If the ligand file with an "org_" prefix is not in the processed ligands directory, 
   ## then that means the output is not valid and should be removed.
   if ! [ -e ../$PROCESSED_DIR/$EXPECTED_PROCESSED_FILE ]; then
      rm $MYFILE;
   else
      ## Otherwise, process the output data and add it to the summary.
      grabOutputData $MYFILE
   fi
}

grabOutputData()
{
   local MYFILE=$1;
   local topRes=$(sed -n '10p' $MYFILE |      ## grab top result row from log file.
                  awk '{print $4}');          ## extract energy value from row. 
   local name=${MYFILE%.txt}                  ## strip off the txt 
   echo -e "$name\t$topRes" >> summary.txt;   ## Output to summary file.
   mv "$MYFILE" "${MYFILE%.pdbqt.txt}.txt";   ## Change log files to *.txt files.
}

## Change to Processed folder to grab zinc ids from original processed files.
cd $PROCESSED_DIR

touch zincs.txt
for f in org_*; do
   grabZincId $f &
done
wait

cd ..


## Change to output folder.
echo "Analysizing the results..."
cd $OUTPUT_DIR
touch summary.txt
for f in *.txt; do
   ensureValidOutputAndProcess $f &
done
wait

## Move over zincs from processed files now so that we don't accidentally
## process it as an output file.
mv ../$PROCESSED_DIR/zincs.txt .

column -t zincs.txt > zinc_cols.txt
column -t summary.txt > sum_cols.txt
## Associate energy to ZINCID by Ligand Names.
sort -k1 -s zinc_cols.txt -o zincs.txt
sort -k1 -s sum_cols.txt -o summary.txt
paste summary.txt zincs.txt > Summary_Final.txt

echo "Sorting the results..."
sort -n -k2 Summary_Final.txt -o Summary_Final.txt

echo "See the 'SortedResult' file in the 'Output' directory."
