from os import system
from sys import argv
print(argv[1])
try:
  iskip=int(argv[2])
except:
  iskip=0

system('rm prova.txt -f && qstat -u %s > prova.txt'%argv[1])

with open('cancel.sh','w') as fo:
  with open('prova.txt','r') as fi:
    l=fi.readline()
    i = 0
    while l:
      if (i-iskip) >= 5:
        #print l.split()[2]  
        fo.write('qdel %s \n'%l.split()[0].split('.')[0])
      l=fi.readline()
      i += 1
system('chmod a+rwx cancel.sh')
system('./cancel.sh')      
