#!/bin/bash

cleanInputFile ()
{
   local FILE=$1;
   local ZINCID=$(grep "ZINC" $FILE |   # Move ZINC Ids to a REMARK, not USER, line.
                  sed 's/USER/REMARK/');
   sed -i -e "1i $ZINCID" -e '/USER/d' -e '/TER/d' $FILE;
}

#Copy over and Ensure all inh_ files don't have unusable things.
cd $1
# Move files in parallel.
# Semaphore used to limit to 100 parallel processes at a time
for f in ligand*.pdbqt; do 
   sem -j100 mv $f inh_$f 
done
sem --wait # Join sub processes.
for f in inh*.pdbqt; do    # Edit files in parallel.
   sem -j100 cleanInputFile $f 
done
sem --wait # Join sub processes.
cd ..