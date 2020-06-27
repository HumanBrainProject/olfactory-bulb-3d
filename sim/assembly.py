from os import system
fo = open('assembly.sh', 'w')
for perc in [0, 50]:
  for g in [78,77,110,105,126,47,29,86,30,24,62,1,125,70,20,15,0,121,115,92,65,55,51,48,120]+[37]:
#    fo.write('./catfiles.sh out-0-%d-g%d-lowcc2\n' % (perc,g))
    fo.write('./catfiles.sh out-25-%d-g%d-li\n' % (perc, g))
fo.close()
system('chmod a+x assembly.sh && ./assembly.sh')
