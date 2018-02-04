#!/usr/bin/env bash

run_batch_loc=~/Capstone/scheduler/runbatch.py

my_cmd=~/random/testfile.sh
misc_dir=~/random/files

my_ssh='calpoly'
remote_dir='~/batchtesting'

input=~/random/input
output=~/random/output

batch_size=1

$run_batch_loc $my_cmd $my_ssh $remote_dir -i $input -o $output --miscdir $misc_dir -b $batch_size
