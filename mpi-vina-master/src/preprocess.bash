#Copy over and Ensure all inh_ files don't have unusable things.
cd $1
for f in ligand*.pdbqt; do # Move files in parallel.
   mv $f inh_$f &
done
wait # Join sub processes.
for f in inh*.pdbqt; do    # Edit files in parallel.
   sed -i -e '/USER/d' -e '/TER/d' $f &
done
wait # Join sub processes.
cd ..
