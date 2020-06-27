fo = open('assembly.sh', 'w')
for sh in [0]:
  for perc in [25,75]:
    for g in [78,77,110,105,126,47,29,86,30,24,62,1,125,70,20,15,0,121,115,92,65,55,51,48,120]:
      fo.write('./catfiles.sh out%d-%d-g%d\n'%(sh,perc,g))
    fo.write('./catfiles.sh out%d-%d\n'%(sh,perc))
fo.close()
