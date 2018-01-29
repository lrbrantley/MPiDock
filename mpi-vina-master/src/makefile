# File      : makefile
# Author    : Md Mokarrom Hossain
# Username  : x2013idf
# Course    : CSCI 522
# Purpose   : makefile in order to ease the compilation procedure.
CC	= mpic++
CCFLAGS	= -std=c++11 -pedantic -Wall -O3
LDFLAGS	= -lmpi

mpiVINA: mpiVINAv2.o CLinkedList.o
	mpicc -o $@ mpiVINAv2.o CLinkedList.o -lmpi
	
mpiVINAv3: mpiVINAv3.o
	$(CC) -o $@ $^ 

mpiVINAv3.o: mpiVINAv3.cpp
	mpic++ -c $(CCFLAGS) mpiVINAv3.cpp $(LDFLAGS)

mpiVINAv4: mpiVINAv4.o
	$(CC) -o $@ $^ 

mpiVINAv4.o: mpiVINAv4.cpp
	mpic++ -c $(CCFLAGS) mpiVINAv4.cpp $(LDFLAGS)


mpiVINAv2.o: mpiVINAv2.c CLinkedList.h
	mpicc -c mpiVINAv2.c
	
CLinkedList.o: CLinkedList.c CLinkedList.h
	mpicc -c CLinkedList.c 

reset:
	rm ./Output/*; rm ./ProcessedLigand/*
clean:
	rm -rf *o mpiVINA
