# File      : makefile
# Author    : Md Mokarrom Hossain
# Username  : x2013idf
# Course    : CSCI 522
# Purpose   : makefile in order to ease the compilation procedure.

mpiVINA: mpiVINAv2.o CLinkedList.o
	mpicc -o $@ mpiVINAv2.o CLinkedList.o -lmpi
	
mpiVINAv3: mpiVINAv3.o CVector.o
	mpicc -o $@ $^ -lmpi

mpiVINAv3.o: mpiVINAv3.c CVector.h
	mpicc -c mpiVINAv3.c

mpiVINAv2.o: mpiVINAv2.c CLinkedList.h
	mpicc -c mpiVINAv2.c
	
CLinkedList.o: CLinkedList.c CLinkedList.h
	mpicc -c CLinkedList.c 

CVector.o: CVector.c CVector.h
	mpicc -c CVector.c
	
reset:
	rm ./Output/*; mv ./ProcessedLigand/* ./Ligand/
clean:
	rm -rf *o mpiVINA