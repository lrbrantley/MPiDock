# MPiDock

This project is designed to allow for the setup and execution of a program (iDock or Autodock Vina) across resources at California Polytechnic San Luis Obispo, noteably the Bishop Cluster and the Massively Parallel Accelerated Computing Lab (MPAC)— Lab 127. 

## Scheduler
At the outermost level, there is the scheduler, written as a command line interface for crontab. The scheduler would then call the batcher, a program which divides up input files and then executes commands remotely with those input files.

## Batcher
The batcher executes the lab manager on a machine within Cal Poly’s MPAC Lab, which sets up an MPI Cluster from the lab computers.
 
## Lab Manager
The lab manager then executes MPiDock, an MPI wrapper for the iDock molecular docking program. Multiple instances of iDock are executed on each machine and the output is then stored and processed by the lab manager. 

## Accuracy Script
This script will allow a user to compare the output logs from two runs of iDocks, two runs of Vina, or iDocks against Vina. The logs will only compare overlapping ligands. 

The -a flag can be any float, but iDock only has .00 decimal places and Vina only .0. 

The script will automatically handle either the automatically generated iDock log.csv file format or the iDock_Summary.txt that Lab Manager generates.

Example of use:
./accuracyComparison.py -a .5 -i ./iDock/Location/log.csv -v ./Vina/Location/summary.txt
./accuracyComparison.py -a .25 -i ./iDock/Location/log.csv ./iDoct/Other/Location/iDockSummary.txt
./accuracyComparison.py -a .75 -v ./Vina/Location/summary.txt /Vina/Other/Location/Final_summary.txt
