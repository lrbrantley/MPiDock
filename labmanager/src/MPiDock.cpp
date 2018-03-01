/*  File      : mpiDock.cpp
 *  Author    : Derek Nola
 *  Course    : CPE 450
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <assert.h>
#include <math.h>

#include <string>
#include <fstream>
#include <vector>
#include <iostream>
#include <chrono>


#include <mpi.h>

#define MASTER                  0

#define COMPUTE_TAG             11
#define TERMINATE_TAG           22
#define WORK_REQ_TAG            33

#define LIGAND_FILE_NAME        "ligandList"

using std::string;

typedef std::chrono::time_point<std::chrono::system_clock> timePoint;

void fillList(std::vector<string> &ligandList);
void mpiDockManager (int numProcs, int ratio, timePoint startTime);
void mpiDockWorker (int workerId);

MPI_Datatype MPI_LIGAND;
string ligandDir, outputDir, processedDir;
std::vector<string> ligandList;



int main(int argc, char *argv[]) {
    int numProcs, rank, ratio;
    
    timePoint startTime = std::chrono::system_clock::now();

    MPI_Init (&argc, &argv );
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &numProcs);

    std::vector<string> allArgs(argv, argv + argc);
    ligandDir 		= allArgs[1]; 	// Default is Ligand folder
    outputDir 		= allArgs[2]; 	// Default is Output folder
    processedDir 	= allArgs[3]; 	// Default is Proccessed folder
    ratio 			= stoi(allArgs[4]);	// Default is 2
    
    if(rank == MASTER) {
    	printf("Master : There are %d workers.\n", numProcs-1);
    	printf("Master : Reading ligandlist file and dividing work.\n");
    }
    
    // All processors will read the ligandlist file and will make the work pool.
    fillList(ligandList);

    if(rank == MASTER){
    	printf("Master : There are %d ligands.\n", (int) ligandList.size());
        mpiDockManager(numProcs - 1, ratio, startTime);
    }
    else{
        mpiDockWorker(rank);    
    }

    MPI_Finalize();
    return 0;
}

void fillList(std::vector<string> &ligandList){

	std::ifstream ligandListFile;
	ligandListFile.open(LIGAND_FILE_NAME);

    if ( !ligandListFile.is_open()) {
    	fprintf(stderr, "Couldn't open file %s for reading.\n", LIGAND_FILE_NAME);
        MPI_Abort(MPI_COMM_WORLD, 911); //Terminates MPI execution environment with error code 911.
        return;
    }
    std::string line;
    while (getline(ligandListFile, line)) {
        // Add ligand to the list.
        ligandList.push_back(line);
    }
}

void mpiDockWorker(int workerId) {
    
    std::string ligandName;
    unsigned int blkSize, start, end;
    timePoint ligandStartTime, ligandEndTime; 
    int offset;
    MPI_Status wStatus;
    // Recieve size of work blocks
    MPI_Bcast(&blkSize, 1, MPI_UNSIGNED, 0, MPI_COMM_WORLD);
    if(workerId == 1){
    	printf("Worker %d: Recieved blkSize %d\n", workerId, blkSize);
    }
    MPI_Barrier(MPI_COMM_WORLD);

    // Initial request to manager for work block
    MPI_Send(NULL, 0, MPI_INT, 0, WORK_REQ_TAG, MPI_COMM_WORLD);
    MPI_Recv(&offset, 1, MPI_INT, 0, MPI_ANY_TAG, MPI_COMM_WORLD, &wStatus);

    while (wStatus.MPI_TAG == COMPUTE_TAG)
    {
        start = blkSize*offset;
        end = (blkSize+start< ligandList.size())? blkSize+start : ligandList.size();
        printf("Worker %d: Started on %u to %u (Offset %d).\n", 
            workerId, start, end - 1, offset);

        for(unsigned int i = start; i < end; i++) {
        	ligandStartTime = std::chrono::system_clock::now();
        	ligandName = ligandList[i];
            printf("Worker %d: Ligand '%u' is processing...\n", workerId, i);
            fflush(stdout);
	        // Setup the iDock command
	        std::string iDockCmd = "./src/iDock/idock --config ./src/iDock/idock.conf --ligand ";
	        iDockCmd.append(ligandDir + "/" + ligandName);
	        iDockCmd.append(" --out " + processedDir);
	   		iDockCmd.append(" --threads 6");
	        iDockCmd.append(" > " + outputDir + "/" + ligandName + ".txt");
	        // Call iDock to perform molecular docking.
	        system(iDockCmd.c_str());

	        iDockCmd.clear();
	        iDockCmd.append("mv " + ligandDir + "/" + ligandName);
	        iDockCmd.append(" " + processedDir + "/" + "org_" + ligandName);
	        // Move processed ligands to ProcessedLigand directory.
	        system(iDockCmd.c_str());

	        ligandEndTime = std::chrono::system_clock::now();
    		std::chrono::duration<double> elapsed = ligandEndTime - ligandStartTime;
    		
    		// If it takes more than 1 minute to process 
    		// a ligand, warn the user that this node is slow.
    		if(elapsed.count() > 60){
    			int len = 0;
    			char nodeName[100];
    			MPI_Get_processor_name(nodeName, &len);
    			nodeName[len] = 0; // Ensure null terminated string
    			fprintf(stderr, 
    				"WARNING: Node '%s' is slow, consider avoiding in future batches.\n", 
    				nodeName);
    		}
        }

        // Request next work block
        MPI_Send(NULL, 0, MPI_INT, 0, WORK_REQ_TAG, MPI_COMM_WORLD);
        MPI_Recv(&offset, 1, MPI_INT, 0, MPI_ANY_TAG, MPI_COMM_WORLD, &wStatus);
    }

    if (wStatus.MPI_TAG == TERMINATE_TAG){
    	if( workerId > (int)ligandList.size()){
    		printf("Worker %d: Not Used, Terminated.\n", workerId);
    	}
    	else{
        	printf("Worker %d: Terminated.\n", workerId);
        }
        fflush(stdout);
    }
    else{
        printf("Worker %d: Received invalid Tag.\n", workerId);
        fflush(stdout);
    }

    MPI_Barrier(MPI_COMM_WORLD);
    return;
}

void mpiDockManager(int numWorkers, int ratio, timePoint startTime) {
    
    std::string ligandName;
    int index = 0, list_len, rem;
    unsigned blkSize;
    MPI_Status mStatus;

    list_len = ligandList.size();

    blkSize = list_len / (numWorkers * ratio);
    blkSize = (blkSize < 1)? 1 : blkSize;

    // Send out inital value of block size
    MPI_Bcast(&blkSize, 1, MPI_UNSIGNED, 0, MPI_COMM_WORLD);
    printf("Master : Sent blkSize %d\n", blkSize);
    MPI_Barrier(MPI_COMM_WORLD);

 
    // Wait for work requests
    // Respond with proper index
    int end = (int)(ligandList.size()/blkSize) + 1;

    int part = 1;
    while(index < end){
        MPI_Recv(NULL, 0, MPI_INT, MPI_ANY_SOURCE, 
            WORK_REQ_TAG, MPI_COMM_WORLD, &mStatus);
        MPI_Send(&index, 1, MPI_INT, mStatus.MPI_SOURCE, 
                COMPUTE_TAG, MPI_COMM_WORLD);
        index++;
        rem = (index*100) / end;
        if(rem > (10 * part) - 1){
        	part++;
       		fprintf(stderr, "Master : Launched %d%%\n", rem);
        }
    }

    //Send out terminate commands
    for(int i = 0; i < numWorkers; i++){
        MPI_Recv(NULL, 0, MPI_INT, MPI_ANY_SOURCE, 
            WORK_REQ_TAG, MPI_COMM_WORLD, &mStatus);
        MPI_Send(NULL, 0, MPI_INT, mStatus.MPI_SOURCE, 
                TERMINATE_TAG, MPI_COMM_WORLD);

    }
    
    MPI_Barrier(MPI_COMM_WORLD);
    sleep(1); //Allow stdout buffer to empty
    timePoint endTime = std::chrono::system_clock::now();
    std::chrono::duration<double> elapsed = endTime- startTime;
    printf("\n\n..........................................\n");
    printf("   Number of workers       = %d \n", numWorkers);
    printf("   Number of Ligands       = %u \n", list_len);
    printf("   Total time required     = %.2lf seconds.\n", elapsed.count());
    printf("..........................................\n\n");
    fflush(stdout);
}