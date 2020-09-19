# -*- coding: utf-8 -*-
'''
OdorStim supplies an odors[name] stimulus to each mitral tuft dendrite
defined by odors[name].glom_weights. Thus there is a separate NetCon for
each tuft dendrite on this process.
'''
from common import *
import params
import odors
from gidfunc import mgid2glom, ismitral, ismtufted
tufts_diverged = {}
import gidfunc

#''' diverge the orn touching the tufts '''
#def init_tufts_diverged():
#  tufts_diverged.clear()
#  N_Mc = params.Nmitral_per_glom
#  N_mTc = params.Nmtufted_per_glom
#  gid_mTc = params.gid_mtufted_begin
#  
#  for glomid in range(params.Ngloms):
#    
#    import mcgrow
#    for gid in range(glomid*N_Mc, (glomid+1)*N_Mc):
#      ntft = int(params.ranstream(gid, params.stream_tuft).discunif(mcgrow.n_min_tuft, mcgrow.n_max_tuft))
#      for i in range(ntft):
#        tufts_diverged[(gid, i)] = params.cellid2glomid(gid)
#
#    import mtcgrow
#    for gid in range(glomid*N_mTc+gid_mTc, (glomid+1)*N_mTc+gid_mTc):
#      ntft = int(params.ranstream(gid, params.stream_tuft).discunif(mtcgrow.n_min_tuft, mtcgrow.n_max_tuft))
#      for i in range(ntft):
#        tufts_diverged[(gid, i)] = params.cellid2glomid(gid)
#
#  # diverge uniformly
#  keys = tufts_diverged.keys()
#  while len(keys) > 1:
#    j = int(params.ranstream(*keys[0]).discunif(1, len(keys)-1))
#    aux = tufts_diverged[keys[0]]
#    tufts_diverged[keys[0]] = tufts_diverged[keys[j]]
#    tufts_diverged[keys[j]] = aux
#    del keys[0]

  
''' OdorStimHelper is implemented in ostimhelper.mod and provides an
    alternative to using the interpreter during the simulation run to
    turn on the odors.  And so will work with CoreNEURON.
'''
use_OdorStimHelper = True
h.net_receive_on_orn = 1.0 if use_OdorStimHelper else 0.0
 
allow_prcellstate_debug = True
''' Debugging differences between the new and old style is difficult when
    prcellstate has
    non-identical cell layout (existence of OdorStimHelper, existence of
    NetCons connecting OdorStimHelper to orn, orn parameter or weight
    differences merely due to on vs off). Hence the on vs off via the
    GLOBAL net_receive_on_orn. With allow_prcellstate_debug = True,
    cell layout is identical in either case
    and discrepancies point to substantive differences. But comes at the
    cost of setting up the new style regardless of whether it is being used
    or not.  Meanwhile, if there are differences between spike rasters
    of a version prior to existence of OdorStimHelper and this
    net_receive_on_orn = 0.0, then it is difficult to take advantage of
    prcellstate.
'''

class OdorStim:
  def __init__(self, odorname, start, dur, conc):
    ''' Specifies the odor for an OdorStim. Note that the OdorStim is
      activated with setup which can only be called after the mitrals
      dict exists (usually from determine_connections.py).
    ''' 
    if rank == 0:
      print(("OdorStim %s start=%g dur=%g conc=%g"%(odorname, start, dur, conc)))
    self.odorname = odorname
    self.start = start
    self.dur = dur
    self.conc = conc
    self.verbose = True
    self.next_invl = 0
    
    if params.glomerular_layer == 0:
      self.w_odor = odors.odors[odorname].getORNs(conc) # odor vector
    elif params.glomerular_layer == 1:
      self.w_odor = odors.odors[odorname].afterPG_1(conc) # odor vector
    elif params.glomerular_layer == 2:
      self.w_odor = odors.odors[odorname].afterPG_2(conc) # odor vector

    # set up the netcons to stimulate the ORNs
    self.netcons = {}
    if not use_OdorStimHelper:
      self.rng_act = params.ranstream(0, params.stream_orn_act)
      self.rng_act.uniform(params.sniff_invl_min, params.sniff_invl_max)
    
    model = getmodel()
    self.src = None
    if use_OdorStimHelper or allow_prcellstate_debug:
      src = h.OdorStimHelper()
      src.start = start
      src.dur = dur
      src.invl_min = params.sniff_invl_min
      src.invl_max = params.sniff_invl_max
      src.noiseFromRandom123(0, params.stream_orn_act, 0)
      self.src = src
    for gid, cell in list(model.mitrals.items()): 
      peak = self.w_odor[mgid2glom(gid)]
      if gidfunc.ismitral(gid):
        g_e_baseline = params.orn_g_mc_baseline
        std_e = params.orn_g_mc_std
        g_e_max = params.orn_g_mc_max
      else:
        g_e_baseline = params.orn_g_mt_baseline
        std_e = params.orn_g_mt_std
        g_e_max = params.orn_g_mt_max

      if h.section_exists("tuftden", 0, cell):
        for i in range(int(cell.ornsyn.count())):
          nc = h.NetCon(self.src, cell.ornsyn.o(i))
          self.netcons[(gid, i)] = nc
          # NetCon weights are peak, base, gemax, stde
          nc.weight[0] = peak
          nc.weight[1] = g_e_baseline
          nc.weight[2] = g_e_max
          nc.weight[3] = std_e
          nc.delay = 0.0

    if use_OdorStimHelper:
      pass
    else:
      self.fih = h.FInitializeHandler(0, (self.init_ev, (start,)))

    

  def init_ev(self, start):
    ''' first event at start.
        In principle this can be called by the user during a simulation
        but if h.t < the previous stop, the randomness will be mixed
        between the multiple (start,stop) intervals.
    '''
    h.cvode.event(start, (self.ev, (start,)))


    
  def ev(self, time):
    ''' set odors stimulation intensity '''
    model = getmodel()
    for gid, cell in list(model.mitrals.items()):
      
      if gidfunc.ismitral(gid):
        g_e_baseline = params.orn_g_mc_baseline
        std_e = params.orn_g_mc_std
        g_e_max = params.orn_g_mc_max
      else:
        g_e_baseline = params.orn_g_mt_baseline
        std_e = params.orn_g_mt_std
        g_e_max = params.orn_g_mt_max
        
      if h.section_exists("tuftden", 0, cell):
        for i in range(int(cell.ornsyn.count())):
          cell.ornsyn.o(i).cc_peak = self.w_odor[mgid2glom(gid)]
          cell.ornsyn.o(i).g_e_baseline = g_e_baseline
          cell.ornsyn.o(i).g_e_max = g_e_max
          cell.ornsyn.o(i).std_e =  std_e
    
    for nc in list(self.netcons.values()):
      nc.event(h.t)

    if self.verbose and rank == 0:
      print('activation of %s at %g (ms)\tinterval %g' % (self.odorname, time, self.next_invl))

    # set up for next sniff
    self.next_invl = self.rng_act.repick()
    if (time + self.next_invl) < (self.start + self.dur):
      h.cvode.event(time+self.next_invl, (self.ev, (time+self.next_invl,)))
    





# init diverged tufts
#init_tufts_diverged()

if __name__ == '__main__':
  h.load_file("nrngui.hoc")
  import common
  common.nmitral = 2
  common.ncell = 10
  import determine_connections
  import odors
  ods = OdorStim(odors.odors['Apple'])
  ods.setup(determine_connections.mitrals, 10., 20., 100.)
  h.tstop = 150
  h.run()
  print('t=', h.t)
