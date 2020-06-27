from neuron import h
import util
import params
import split
from gidfunc import *
tvec = h.Vector()
vmrecordings = []
    
def record(gid, secid=None, arc=None):
  sec = None
  if ismitral(gid):
    if not secid:
      sec = split.msoma(gid)
      arc = 0.5
    elif secid == -1:
      sec = split.mpriden(gid)
    else:
      sec = split.msecden(gid, secid)
      
  elif ismtufted(gid):
    if not secid:
      sec = split.msoma(gid)
      arc = 0.5
    elif secid == -1:
      sec = split.mpriden(gid)
    else:
      sec = split.msecden(gid, secid)
      
  elif isgranule(gid):
    if not secid:
      sec = split.gsoma(gid)
      arc = 0.5
    else:
      sec = split.gpriden(gid, secid)

  if sec:
    tvec.record(h._ref_t)
    
    filename = '%d'%gid
    if secid:
      filename += '-%d'%secid
    if arc:
      filename += '-%g'%arc
    filename += '.txt'
    filename = params.filename+'-'+filename
    vmrec = h.Vector()
    vmrec.record(sec(arc)._ref_v)
    vmrecordings.append((vmrec, filename))
    


def output():
  wtime = h.startsw()
  for vmrec, filename in vmrecordings:
    f = open(filename, 'w')
    for j in range(int(vmrec.size())):
      f.write('%g %g\n'%(tvec.x[j], vmrec.x[j]))
    f.close()
  util.elapsed('vm recorded  write time %.g'%(h.startsw()-wtime))
  
