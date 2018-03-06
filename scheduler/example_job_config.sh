#!/usr/bin/env bash

# This is where you have the batcher.py python script
batcher_loc=~/distdrugdisc/scheduler/batcher.py

# This is the LOCAL location of the command to run.
my_cmd=~/zika/run_labmngr.sh
# This is the directory of extra files to send over.
# Inside of it we'll place in the LABMNGR, mpiVina, Autodock Vina, receptor molecule, etc.
misc_dir=~/zika/iDock

# This is an ssh alias, you could be explicit with 'user@remote_address' as well.
my_ssh='javalab' 
# This is where we'll be placing the files on the remote host.
remote_dir='~/zika_processing' 

# This is the LOCAL location of the Input Ligands
input=~/zika/Ligands
# This is the LOCAL location of where Output will be transferred back to.
output=~/zika/Output

# This is the prefix of the files we place into ProcessedLigands
prefix='inh_'

# This is the setting for how many to batch at once. Recommended is ~25k.
batch_size=100
# Time limit in HOURS for when to stop sending batches.
timelimit=8

# Actually running the runbatch.py script.
$batcher_loc $my_cmd $my_ssh $remote_dir --input $input --output $output\
      --batch $batch_size --timeout $timelimit --miscdir $misc_dir --processedPrefix $prefix\
      --processedFilesModified
