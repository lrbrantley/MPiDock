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
for f in ligand*.pdbqt; do # Move files in parallel.
   mv $f inh_$f &
done
wait # Join sub processes.
for f in inh*.pdbqt; do    # Edit files in parallel.
   cleanInputFile $f &
done
wait # Join sub processes.
cd ..