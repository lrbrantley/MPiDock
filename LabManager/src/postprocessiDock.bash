#!/bin/bash

## This makes it so that empty wildcard expansions are null rather than literals.
shopt -s nullglob

OUTPUT_DIR=$1
PROCESSED_DIR=$2

## iDock instances killed early still output some bad data, this gets
## rid of those files so that they don't screw up the summary.
## ASSUMES you're in the output directory!!!!
ensureValidOutputAndProcess()
{
   local MYFILE=$1;
   local LIGAND_NAME=${f%.txt};
   local EXPECTED_ORG_FILE=org_$LIGAND_NAME;
   ## If the ligand file with an "org_" prefix is not in the processed ligands directory, 
   ## then that means the output is not valid and should be removed.
   if ! [ -e ../$PROCESSED_DIR/$EXPECTED_ORG_FILE ]; then
      echo "ERROR $LIGAND_NAME PROCESSING DID NOT COMPLETE SUCCESSFULLY"
      rm $MYFILE; ## Remove bad output.
      rm ../$PROCESSED_DIR/$LIGAND_NAME; ## Remove potential bad (incomplete) output from Processed folder, which could screw up the batcher.

   else
      ## Otherwise, process the output data and add it to the summary.
      local topRes=$(sed -n '10p' $MYFILE |      ## grab top result row from log file.
                     awk '{print $4}');          ## extract energy value from row. 
      mv "$MYFILE" "${MYFILE%.pdbqt.txt}.txt";   ## Change log files to *.txt files.

      ## Get ZINC ID from original file.
      local zincId=$(grep "Name" $EXPECTED_ORG_FILE | uniq | awk '{print $4}');
      echo -e "$LIGAND_NAME\t$topRes\t$LIGAND_NAME\t$zincId" >> summary.txt;   ## Output row to file.
   fi
}

## Change to output folder.
echo "Analysizing the results..."
cd $OUTPUT_DIR
for f in *.txt; do
   ensureValidOutputAndProcess $f &
done
wait

## Makes a summary file just in case it doesn't already exist.
touch summary.txt

column -t summary.txt > Summary_Final.txt

echo "Sorting the results..."
sort -n -k2 Summary_Final.txt -o Summary_Final.txt

echo "See the 'Summary_Final.txt' file in the 'Output' directory."
