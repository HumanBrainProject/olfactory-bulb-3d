#!/bin/bash
#if [ -a $1.sbgh.0 ] 
#then 
printf 'assembling...'

# assembly header and data
cat $1.sbgh.* > $1.header
rm -f $1.sbgh.*

printf "from struct import pack\nfrom os import path\nf=open('"$1".size','wb')\nf.write(pack('>q', path.getsize('"$1".header')))\nf.close()\nquit()" > wd.py
python wd.py
rm -f wd.py

cat $1.sbg.* > $1.data
rm -f $1.sbg.*

cat $1.size $1.time $1.header $1.data > $1.spk2
rm -f $1.time 
rm -f $1.size $1.header $1.data

# assembly weights
cat $1.weight.dat.* > $1.weight.dat
rm -f $1.weight.dat.*

# assembly dictionary
cat $1.dic.* > $1.dic
rm -f $1.dic.*


# assembly text history
#cat $1.spikes.dat.* > $1.spikes.dat
#rm $1.spikes.dat.*
#rm $1.spikes.dat

printf 'done\n'
#else
#printf 'file does not exist\n'
#fi
