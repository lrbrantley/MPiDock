# File      : makefile
# Author    : Derek Nola
# Course    : CPE 450
CC	= mpic++
CCFLAGS	= -std=c++11 -pedantic -Wall -O2
LDFLAGS	= -lmpi

MPIVina: MPIVina.o
	$(CC) -o ../$@ $^ 

MPIVina.o: MPIVina.cpp
	mpic++ -c $(CCFLAGS) MPIVina.cpp $(LDFLAGS)

MPiDock: MPiDock.o
	$(CC) -o ../$@ $^ 

MPiDock.o: MPiDock.cpp
	mpic++ -c $(CCFLAGS) MPiDock.cpp $(LDFLAGS)

reset:
	rm ../Output/*; rm ../ProcessedLigand/*
clean:
	rm -rf *o ../MPIVina ../MPiDock
