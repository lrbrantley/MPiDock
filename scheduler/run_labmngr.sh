#!/usr/bin/env bash

timeout=''

# check if we have a timeout flag sent to us
while getopts 't:' flag; do
   case "${flag}" in
      t) timeout="${OPTARG}" ;;
      *) error "Unexpected option ${flag}" ;;
   esac
done

unpackagePackage ()
{
   # Move files out to place we need them to be.
   mv Vina/LABMNGR.py . 
   mv Vina/*.pdbqt .
   mv Vina/*process.bash .
   # Have to move cpp out since it expects to be recompiled each time.
   mv Vina/makefile .
   mv Vina/mpiVINAv4.cpp .
}

if [ -z "$timeout" ]; then 
   $timeout='-1'
fi

# Run LABMNGR
./LABMNGR.py -l ./Ligand -o ./Output -p ./ProcessedLigand -t $timeout < 100 
