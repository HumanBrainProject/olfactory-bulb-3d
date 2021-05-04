from column_eval import column_eval, preprocess, axial_score, radial_score
from column_affecting_score import affecting_score as cas
import column_affecting_score as casm
casm.cas = {}
fi=open('imp.txt','r')
imp={}
line=fi.readline()
while line:
  tk=line.split()
  imp[int(tk[0])]=float(tk[1])
  line=fi.readline()
fi.close()

gli = [ (74, 100), (84, 52), (21, 102), (33, 124), \
        (106, 59), (89, 111), (113, 78), \
        (108, 87), (105, 18), (112, 7), (25, 29), \
        (94, 22), (86, 117), (49, 116), (107, 83) ]


#data = preprocess('g37e1i002step3.weight.dat')
#print radial_score(data, 37), axial_score(data, 37)

data = preprocess('g37cc030s2.weight.dat')
ce1 = column_eval(data, 37)[0][1]

#print radial_score(data, 37), axial_score(data, 37)
  
from math import log
index = 0
fo = open('output1.txt', 'w')
for i in range(1, 5):
  jmax=4
  if i==2:
    jmax -= 1
  
  for j in range(0, jmax):

    gl1, gl2 = gli[index]
    data = preprocess('odpart%d_%d.weight.dat' % (i, j))

    #print radial_score(data, 37), axial_score(data, 37)
    
    ce = column_eval(data, 37)[0][1]
    ri = (imp[gl1] + imp[gl2])/2 #)-imp[37])/imp[37]
    x = cas(37,gl1,gl2) #log(cas(37,gl1,gl2)/((cas(gl1,37,gl2)+cas(gl2,37,gl1))/2.0))
    print(i, j, gl1, gl2, x, ri, ce)
    fo.write('%d %d %g %g %g\n'%(gl1, gl2, x, ri, ce[0]))
    index += 1
fo.close()
