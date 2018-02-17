Testing Files for iDock and Vina
===

KnownHit.pdbqt
* ligand 20_33523
* Highest of the known hits

KnownHit.mol2
* File type difference. Another common format. 

KnownMiss.pdbqt
* Glucose
* Definetly a miss, should never be close to the top

KnownMiss.mol2
* File type difference. Another common format. 

PoisonLigand.pdbqt
* Boron Atom
* Should break

PoisonLigand.mol2
* File type difference. Another common format. 

ProblemHit.pdbqt
* Known Hit - ligand 5T1V
* When run with the staticly compilied version, no error
* Dynamic compiled, assertion error

ProblemHit.mol2
* File type difference. Another common format. 

Receptor.mol2
* The same receptor with a different format. 

Corrupt Files
---

All corrupt known hit files are varients on 20_33523. 

CorruptKnownHit
* Inital remarks removed

CorruptKnownHit2
* Root section removed

CorruptKnownHit3
* 1st Branch section removed

CorruptKnownHit4
* 2nd Branch section removed

CorruptKnownHit5
* Branch sections combine

CorruptKnownHit6
* TORSDOF statement at the end removed

CorruptKnownHit7
* EndRoot statement removed

CorruptKnownHit8
* 1st End Branch statement removed

CorruptKnownHit9
* 2nd End Branch statement removed

CorruptKnownHit10
* pdbqt file mislabeled as a mol2

CorruptKnownHit11
* mol2 file mislabeled as a pdbqt

CorruptKnownHit12
* Root statement removed

CorruptKnownHit13
* 1st Branch statement

CorruptFile
* pdbqt file with only the output of a result from idock
