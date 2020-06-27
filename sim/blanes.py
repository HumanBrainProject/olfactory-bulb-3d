from common import *
import gidfunc
import params
import misc
import geodist
from math import exp
from util import elapsed
import params
h.load_file('blanes.hoc')

def load_blanes_dic(filename):
    ggids_here = getmodel().granules.keys()
    blanes_here = set([x[1] for x in params.glom2blanes ])
    import struct
    with open(filename, 'rb') as fi:
        rec = fi.read(24)
        while rec:
            ggid, blanesgid, w = struct.unpack('>QQQ', rec)
            if ggid in ggids_here and blanesgid in blanes_here:
                yield ggid, blanesgid, w
            rec = fi.read(24)

            

def mkblanes(gid):
    return h.Blanes()

def mk_gl2b_connections():
  getmodel().mt2blanes_connections.clear()
  for x in params.glom2blanes:
    if len(x) == 2:
      glomid, blanes_gid = x
      w = None
    else:
      glomid, blanes_gid, w = x
    if blanes_gid not in getmodel().blanes.keys():
      continue
    for mtgid in range(glomid*params.Nmtufted_per_glom+params.gid_mtufted_begin, (glomid+1)*params.Nmtufted_per_glom+params.gid_mtufted_begin):
      getmodel().mt2blanes_connections.add((mtgid, blanes_gid, w))
  elapsed('%d middle tufted to blanes connections generated' % pc.allreduce(len(getmodel().mt2blanes_connections),1))
    
class mt2blanes:
    def __init__(self, mgid, blanesgid, w=None):
        self.mgid = mgid
        self.blanes_gid = blanesgid
        self.blanes_cell = getmodel().blanes[blanesgid]


        rng = params.ranstream(blanesgid, params.stream_blanes+gidfunc.mgid2glom(mgid))
        
        ibranch = int(rng.discunif(0, self.blanes_cell.nden0-1))
        idend = int(rng.discunif(0, self.blanes_cell.nden1-1))
        x = rng.uniform(0,1)

        
        self.syn = h.Exp2Syn(self.blanes_cell.dend[ibranch][idend](x))
        self.syn.e = 0
        self.syn.tau1 = 1
        self.syn.tau2 = 250
        self.nc = pc.gid_connect(mgid, self.syn)
        if w:
          self.nc.weight[0] = w
        else:
          self.nc.weight[0] = params.mt2bc_exc_gmax
        self.nc.delay = 1
        self.gid = gidfunc.mbs_gid(mgid, blanesgid)
        #pc.set_gid2node(self.gid, pc.id())
        
    def wstr(self):
        return '%d %d %g\n'%(self.gid, self.nc.weight[1], self.nc.weight[2]*self.syn.gmax)
    
class blanes2granule:
    def __init__(self, blanesgid, ggid, w=1):
        
        self.ggid = ggid
        self.blanes_gid = blanesgid
        self.granule_cell = getmodel().granules[ggid]


        rng = params.ranstream(blanesgid, params.stream_blanes+params.Nmtufted+ggid)
        L = self.granule_cell.priden2[0].L * rng.uniform(0, 1)
        if L <= self.granule_cell.priden2[0].L:
            sec = self.granule_cell.priden2[0]
            x = L/self.granule_cell.priden2[0].L
            
        self.syn = h.Exp2Syn(sec(x))
        self.syn.e = -80
        self.syn.tau1 = 1
        self.syn.tau2 = 15

        self.nc = pc.gid_connect(self.blanes_gid, self.syn)
        self.nc.weight[0] = w*params.bc2gc_inh_gmax
        self.nc.delay = 1

        self.gid = gidfunc.bc2gc_gid(blanesgid, ggid)
        #pc.set_gid2node(self.gid, pc.id())
        
    def wstr(self):
        return '%d %d %g\n'%(self.gid, self.nc.weight[1], self.nc.weight[2]*self.syn.gmax)


    
def mk_b2g_connections():
#    gid_blanes_existing = set([x[1] for x in params.glom2blanes ])
    getmodel().blanes2gc_connections.clear()
    elapsed('\t%d granules are generated' % pc.allreduce(len(getmodel().granules),1))
    for ggid, blanes_gid, factor in load_blanes_dic('blanes6.dic'):
      getmodel().blanes2gc_connections.add((ggid, blanes_gid, factor))

#    for ggid in getmodel().granules:
#      for blanes_gid in gid_blanes_existing:
#        getmodel().blanes2gc_connections.add((ggid, blanes_gid))
    elapsed('%d blanes to granule connections generated' % pc.allreduce(len(getmodel().blanes2gc_connections),1))











        
