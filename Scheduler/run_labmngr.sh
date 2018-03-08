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
   # Everything in the Misc directory should be moved out.
   mv Misc/* .
}

if [ -z "$timeout" ]; then 
   timeout='-1'
fi

# first unpackage the package.
unpackagePackage
# Run LABMNGR the echo 100 pipe is the number of hosts to use.
echo 100 | ./LABMNGR.py -l ./Ligands -o ./Output -p ./ProcessedLigands -t $timeout -v
