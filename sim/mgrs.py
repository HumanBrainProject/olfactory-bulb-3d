'''
mitral-granule reciprocal synapse

patterned after mgrs.hoc of the bulb3test model but allow any number of
secondary dendrite processes (indexed by mitral.secden[i]).  Ie a
connection is defined (in python) by the 6 tuple (mitral_gid,
secden_index, x, granule_gid, priden_index, x). Connection algorithms
allow more than one mgrs with the same mitral and granule.
Therefore, when the function map from (mgid, ggid) to synapse_gid is used,
it may be necessary to do futher disambiguation.
'''

from common import *
from gidfunc import mgrs_gid, ismitral, ismtufted
from params import gid_mgrs_begin

import split
nmitral = params.Nmitral
ngranule = params.Ngranule
ngloms = params.Ngloms
nmxg = params.Nmitral_per_glom

from lateral_connections import gc_is_superficial as gcissup

from dsac import *



class MGRS:
  '''From a mitral and granule synapse location, and consistent with what
     exists on this process, construct the 5 parts of the reciprocal synapse.
     If the granule location exists, then a spine, ThreshDetect, and
     AmpaNmda synapse will be created. If the mitral location exists, then
     a ThreshDetect and FastInhib synapse will be created. The appropriate gid
     for the ThreshDetect instances will be registered. And the appropriate
     NetCons will connect to the synapses.
  '''
  '''
     To allow use of the FastInhibSTDP synapse on the Mitral side of the
     MGRS, there is an additional part which is a negative weight netcon
     connecting from the mitral side ThreshDetect to the FastInhibSTDP
     instance which provides the post synaptic spike timing information.
     There are major administrative differences due to the weight vector
     differences between FastInhib and FastInhibSTDP.
  '''

  def __init__(self, mgid, isec, xm, ggid, ipri, xg, slot):
    self.mgid = mgid
    self.ggid = ggid
    self.slot = slot
    self.xm = xm
    self.xg = xg
    self.isec = isec
    self.ipri = ipri
    
    self.msecden = split.msecden(mgid, isec)
    self.gpriden = split.gpriden(ggid, ipri)
    self.md_gid = mgrs_gid(mgid, ggid)
    self.gd_gid = mgrs_gid(ggid, mgid)
    self.md = None #ThreshDetect on mitral
    self.gd = None #ThreshDetect on granule
    if params.use_fi_stdp:
      self.fi = None #FastInhibSTDP on mitral
      self.postspike2fi = None # negative weight NetCon from md to fi
    else:
      self.fi = None #FastInhib on mitral
    self.ampanmda = None #AmpaNmda on granule
    self.gd2fi = None #NetCon to fi
    self.md2ampanmda = None #NetCon to ampanmda

    if pc.gid_exists(self.md_gid) > 0. or pc.gid_exists(self.gd_gid) > 0.:
      print("md_gid=%d and/or gd_gid=%d already registered" % (self.md_gid, self.gd_gid))
      raise RuntimeError

    if self.msecden:
      self.md = h.ThreshDetect(self.msecden(xm))
      if params.use_fi_stdp:
        self.fi = h.FastInhibSTDP(self.msecden(xm))
        nc = h.NetCon(self.md, self.fi)
        self.postspike2fi = nc
        nc.weight[0] = -1
        nc.delay = 1

      else:
        self.fi = h.FastInhib(self.msecden(xm))
        try:
          if params.training_inh:
            self.fi.training = 1
          else:
            self.fi.training = 0
        except:
#          print 'error'
          self.fi.training = 1
          
      if ismitral(mgid):
        self.fi.gmax = params.mc_inh_gmax
        self.fi.tau1 = params.mc_fi_tau1
        self.fi.tau2 = params.mc_fi_tau2
      elif ismtufted(mgid):
        self.fi.gmax = params.mt_inh_gmax
        self.fi.tau1 = params.mt_fi_tau1
        self.fi.tau2 = params.mt_fi_tau2

      pc.set_gid2node(self.md_gid, pc.id())
      pc.cell(self.md_gid, h.NetCon(self.md, None), 1)

    if self.gpriden:
      self.spine = h.GranuleSpine()
      if gcissup(self.ggid):
        self.spine.sup_deep_flag(1)
      else:
        self.spine.sup_deep_flag(0)

      self.spine.neck.connect(self.gpriden(xg))
      
      #self.dsac = dSAC(self.ggid, self.spine)
      
      self.gd = h.ThreshDetect(self.spine.head(0.5))
      self.gd.vthresh = -50
      self.ampanmda = h.AmpaNmda(self.spine.head(0.5))
      if ismitral(mgid):
        self.ampanmda.gmax = params.mc_exc_gmax
      elif ismtufted(mgid):
        self.ampanmda.gmax = params.mt_exc_gmax
      try:
        if params.training_exc:
          self.ampanmda.training = 1
        else:
          self.ampanmda.training = 0
      except:
#        print 'error'
        self.ampanmda.training = 1

      pc.set_gid2node(self.gd_gid, pc.id())
      pc.cell(self.gd_gid, h.NetCon(self.gd, None), 1)

    # Cannot be done above because output ports must exist prior to using 
    # an output gid as an input port on the same process.
    if self.fi:
      self.gd2fi = pc.gid_connect(self.gd_gid, self.fi)
      if params.use_fi_stdp:
        self.gd2fi.weight[0] = 1
      else:
        self.gd2fi.weight[0] = 1 # normalized
        try:
          init_inh_weight = params.init_inh_weight
        except:
          init_inh_weight = 0
        self.gd2fi.weight[1] = init_inh_weight
      self.gd2fi.delay = 1
      
    if self.ampanmda:
      self.md2ampanmda = pc.gid_connect(self.md_gid, self.ampanmda)
      self.md2ampanmda.weight[0] = 1 #normalized
      try:
        init_exc_weight = params.init_exc_weight
      except:
        init_exc_weight = 0
      self.md2ampanmda.weight[1] = init_exc_weight
      self.md2ampanmda.delay = 1

  def pr(self):
    print("%d %d <-> %d %d"%(self.mgid, self.md_gid, self.gd_gid, self.ggid))
    if self.msecden:
      print(self.msecden.name(), self.md.hname(), self.fi.hname(), self.gd2fi.hname(), " ", int(self.gd2fi.srcgid()))
    if self.gpriden:
      print(self.gpriden.name(), self.gd.hname(), self.ampanmda.hname(), self.md2ampanmda.hname(), " ", int(self.md2ampanmda.srcgid()))


  def mg_dic_str(self):
    s = ''
    if self.gd2fi:
      s += '%d %d %d %g %d\n' % (self.gd_gid, self.ggid, self.ipri, self.xg, self.slot)
    if self.md2ampanmda:
      s += '%d %d %d %g %d\n' % (self.md_gid, self.mgid, self.isec, self.xm, self.slot)
    return s

  def wstr(self):
    ''' return string in proper wsfile format '''
    s = ''
    if self.gd2fi:
      s += '%d %g %g\n'%(self.gd_gid, self.sm(), self.wm())
    if self.md2ampanmda:
      s += '%d %g %g\n'%(self.md_gid, self.sg(), self.wg())
    return s

  def sm(self):
    if params.use_fi_stdp:
      return self.fi.wsyn
    else:
      return self.gd2fi.weight[1]
  def sg(self):
    return self.md2ampanmda.weight[1]
  def wm(self):
    if params.use_fi_stdp:
      return self.fi.wsyn * self.fi.gmax
    else:
      return self.gd2fi.weight[2] * self.fi.gmax
  def wg(self):
    return self.md2ampanmda.weight[2] * self.ampanmda.gmax

def mk_mgrs(mgid, isec, xm, ggid, ipri, xg, slot):
  ''' Return MGRS instance if at least on half exists, otherwise None.'''
  if split.msecden(mgid, isec) or split.gpriden(ggid, ipri):
    return MGRS(mgid, isec, xm, ggid, ipri, xg, slot)
  return None
    
def multiple_cnt():
  cnt = 0;
  for mgrs in list(getmodel().mgrss.values()):
    if mgrs.slot != 0: # slot is tuple not integer
      if mgrs.gd: cnt += 1
      if mgrs.md: cnt += 1
  return cnt

if __name__ == "__main__":
  import mkmitral, split
  h.load_file("granule.hoc")

  m = mkmitral.mkmitral(1)
  pieces = split.secden_indices_connected_to_soma(m)
  pieces.append(-1)
  split.splitmitral(1, m, pieces)
  pc.set_gid2node(1, pc.id())
  pc.cell(1, h.NetCon(m.soma(.5)._ref_v, None, sec=m.soma))

  g = h.Granule()
  pc.set_gid2node(10000, pc.id())
  pc.cell(10000, h.NetCon(g.soma(.5)._ref_v, None, sec=g.soma))

  mgrs = MGRS(1, 0, .8, 10000, 0, .1)
  mgrs.pr()
  mgrs2 = MGRS(1, 0, .8, 10000, 0, .1)


