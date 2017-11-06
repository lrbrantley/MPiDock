/*  File      : mpiVinav2.c
 *  Author    : Md Mokarrom Hossain
 *  Username  : x2013idf
 *  Course    : CSCI 522
 *  Purpose   : MPI based parallel version of Autodock Vina.
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <fstream>
#include <string.h>
#include <unistd.h>
#include <assert.h>
#include <vector>
#include <iostream>

#include "mpi.h"

#define MASTER                  0

#define COMPUTE_TAG             11
#define TERMINATE_TAG           22
#define WORK_REQ_TAG            33

#define MAX_LIGAND_NAME_LENGTH  25
#define LIGAND_FILE_NAME        "ligandlist"

void mpiVinaManager (int numProcs);
void mpiVinaWorker (int workerId, int numProcs);

MPI_Datatype MPI_LIGAND;
std::vector<std::string> lgndsList;
std::string ligandDir, outputDir, processedDir;

int main(int argc, char *argv[]) {
    int numProcs, rank, totalLigands;
    std::ifstream ligandListFile;

    double startTime = 0.0, endTime = 0.0;

    MPI_Init (&argc, &argv );
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &numProcs);

    std::vector<std::string> allArgs(argv, argv + argc);
    ligandDir = allArgs[1];
    outputDir = allArgs[2];
    processedDir = allArgs[3];

    // All processors will read the ligandlist file and will make the work pool.
    if(rank == MASTER)
        printf("All processors: Reading ligandlist file and dividing work.\n");
    startTime = MPI_Wtime(); // start timer.
    ligandListFile.open(LIGAND_FILE_NAME);

    if ( !ligandListFile.is_open()) {
        printf("Couldn't open file %s for reading.\n", LIGAND_FILE_NAME);
        MPI_Abort(MPI_COMM_WORLD, 911); //Terminates MPI execution environment with error code 911.
        return 0;
    }
    std::string line;
    while (getline(ligandListFile, line)) {
        //Add to the list.
        lgndsList.push_back(line);
        //std::cout << line << std::endl;
    }
    //Get total number of ligands.
    totalLigands = lgndsList.size();


    mpiVinaWorker(rank, numProcs);    // All other processors will play the role of mpiVINA worker.

    if (rank == numProcs - 1) {
        endTime = MPI_Wtime(); // end timer.
        printf("\n\n..........................................\n");
        printf("   Number of workers       = %d \n", numProcs);
        printf("   Number of Ligands       = %u \n", totalLigands);
        printf("   Total time required     = %.2lf seconds.\n", endTime - startTime);
        printf("..........................................\n\n");
        fflush(stdout);
    }

    MPI_Finalize ( );
    return 0;
}

void mpiVinaManager(int numProcs) {
    int i;
    printf("Manager has started.\n");

    for (i = 1; i < numProcs; i++) {
        printf("Ping Worker %d\n", i);
        MPI_Send(&i, 1, MPI_INT, i, COMPUTE_TAG, MPI_COMM_WORLD);
    }

    //Computation has done. Send termination tag to all the slaves.
    for (i = 1; i < numProcs; i++) {
        MPI_Send(&i, 1, MPI_INT, i, TERMINATE_TAG, MPI_COMM_WORLD);
    }
    return;
}

void mpiVinaWorker(int workerId, int numProcs) {
    
    std::string ligandName;
    int nops, start, end, rem, list_len, i;

    list_len = lgndsList.size();
    // If the number of ligands > number of nodes
    if(list_len < numProcs){
        start = (list_len > workerId)? workerId : 0;
        end = (start)? start+1 : 0;
    }
    else{
        nops =  (list_len / numProcs) + 1;
        rem = list_len % numProcs;
        if(workerId >= rem){
            start = workerId * nops - (workerId - rem);
            end = start + nops - 1;
        }
        else{
            start = workerId * nops;
            end = start + nops;
        }
        //If the last node in cluster finish remainder
        //if((list_len - end) <= rem) end = list_len;
    }

    if (!end) return;

    printf("Worker %d of %d has started on %d to %d.\n", 
            workerId, numProcs, start, end - 1);
    sleep(1);
    for(i = start; i < end; i++) {
        ligandName = lgndsList[i];
        printf("Worker = %d : ligand '%s' is processing...\n", workerId, ligandName.c_str());
        fflush(stdout);

        std::string vinaCmd = "Vina/vina --config Vina/conf.txt --ligand " + ligandDir + "/";
        vinaCmd.append(ligandName);
        vinaCmd.append(" --out " + outputDir + "/");
        vinaCmd.append(ligandName);
        vinaCmd.append(" --log " + outputDir + "/");
        vinaCmd.append(ligandName);
        vinaCmd.append(".txt > /dev/null");
        //Ask Autodock Vina to perform molecular docking.
        system(vinaCmd.c_str());

        vinaCmd.clear();
        vinaCmd.append("mv " + ligandDir + "/");
        vinaCmd.append(ligandName);
        vinaCmd.append(" " + processedDir + "/");
        //Move processed ligands to ProcessedLigand directory.
        system(vinaCmd.c_str());
    }

    printf("Worker %d has terminated.\n", workerId);
    fflush(stdout);

    return;
}
