from neuron import h
import params

h.load_file('mitral.hoc')
h.load_file('mtufted.hoc')
from grow import genMitral, genMTufted
from gidfunc import ismitral, ismtufted, mgid2glom

def mkmitral(gid):
  if ismitral(gid):
    nrn = genMitral(gid)
    m = h.Mitral(gid)
  else:
    nrn = genMTufted(gid)
    m = h.mTufted(gid)


  m.createsec(len(nrn.dend), len(nrn.tuft))

  for i, d in enumerate(nrn.dend):
  
    if d.parent == nrn.soma[0]: 
      m.secden[i].connect(m.soma(.5))
    else:
      index = nrn.dend.index(d.parent)
      m.secden[i].connect(m.secden[index](1)) 
  
  m.geometry() # again to get the hillock stylized shape

  fillall(nrn, m)
  
  m.subsets()
  m.topol() # need to connect secondary dendrites explicitly  
  m.segments() # again to get the proper number of segments for tuft and secden  
  m.memb()

  m.setup_orns(gid, params.stream_orn_w)
  
  if ismitral(gid):
    orn_g_std = params.orn_g_mc_std
    orn_g_baseline = params.orn_g_mc_baseline
    orn_g_max = params.orn_g_mc_max
  elif ismtufted(gid):
    orn_g_std = params.orn_g_mt_std
    orn_g_baseline = params.orn_g_mt_baseline
    orn_g_max = params.orn_g_mt_max

  for i in range(int(m.ntuft)):
    m.ornsyn.o(i).g_e_baseline = orn_g_baseline
    m.ornsyn.o(i).std_e = orn_g_std
    m.ornsyn.o(i).g_e_max = orn_g_max

  if mgid2glom(gid) in params.vclamp:
      m.vcinit()  


  return m

def fillall(n, m):
  fillshape(n.soma[0], m.soma)
  fillshape(n.apic[0], m.priden)
  for i,s in enumerate(n.dend):
    fillshape(s, m.secden[i])
  for i,s in enumerate(n.tuft):
    fillshape(s, m.tuftden[i])
  
def fillshape(s1, s2):
    s2.push()
    h.pt3dclear()
    for x in s1.points:
      h.pt3dadd(x[0], x[1], x[2], x[3])
    h.pop_section()

if __name__ == "__main__":
  cells = []
  x = h.startsw()
  # note 259 has tertiary branches
  for i in range(10):
    print "mid=",i
    cells.append(mkmitral(i))
  print "wall time ", h.startsw() - x, " seconds"
  h.load_file('select.hoc')
  
