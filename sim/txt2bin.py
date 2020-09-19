filename='prova.spikes.dat'
filespk='prova'
from struct import pack

m={}

fi=open(filename,'r')
line=fi.readline()
while line:
  tk=line.split()
  if len(tk)>1:
    t=float(tk[0])
    gid=int(tk[1])
    if gid in m:
      m[gid].append(t)
    else:
      m.update({gid:[t]})
  line=fi.readline()
fi.close()

fo1=open(filespk+'.sbgh','wb')
fo=open(filespk+'.sbg','wb')
for gid, tspks in list(m.items()):
  fo.write(pack('>LL',gid,len(tspks)))
  for x in tspks:
    fo1.write(pack('>f',x))
fo.close()
fo1.close()
from os import path,system
f=open(filespk+'.size','wb')
f.write(pack('>q', path.getsize(filespk+'.size')))
f.close()

system('cat %s.size %s.sbgh %s.sbg > %s.spk'%(filespk,filespk,filespk,filespk))
system('rm %s.size %s.sbgh %s.sbg'%(filespk,filespk,filespk))

quit()
