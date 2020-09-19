from common import *
from loadbalutil import lb
import net_mitral_centric as nmc
from balance import load_bal
from destroy_model import destroy_model
from all2all import all2all
import split
import util
import mgrs
import params
import gidfunc
from gidfunc import ismitral, ismtufted, isgranule, isblanes
from params import Ngranule 
import blanes

  

def determine_multisplit_complexity(model):
  ''' single phase '''
  cxlist = []
  for gid in model.mitrals:
    cxm = split.mitral_complexity(model.mitrals[gid])
    cxlist.append((cxm[1],(gid,-1)))
    for i,cx in enumerate(cxm[2]):
      cxlist.append((cx,(gid,i)))
  for gid in model.granules:
    cxlist.append((lb.cell_complexity(sec=model.granules[gid].soma),(gid,-1)))
  for gid in model.blanes:
    cxlist.append((lb.cell_complexity(sec=model.blanes[gid].soma),(gid,-1)))    
  return cxlist

def multisplit_distrib(model):
  enter = h.startsw()



  
  cxlist = determine_multisplit_complexity(model)
  
  #start over
  destroy_model(model)


  # fake cell to solve problem with gap junctions
#  init_fake_cell()
  
  # but we still have model.mconnections and model.rank_gconnections
  # from the round-robin distribution perspective.
  # we will need to tell the ranks  where to distribute that information

  cxlist = load_bal(cxlist, nhost) #cxlist is the list of (cx,(gid,piece)) we want on this process
  # the new distribution of mitrals and granules
  model.gids = set([item[1][0] for item in cxlist])
  model.mitral_gids = set([gid for gid in model.gids if ismitral(gid) or ismtufted(gid) ])
  model.granule_gids = set([gid for gid in model.gids if isgranule(gid) ])
  model.blanes_gids = set([gid for gid in model.gids if isblanes(gid) ])
  
  # for splitting need gid:[pieceindices]
  gid2pieces = {}
  for item in cxlist:
    gid = item[1][0]
    piece = item[1][1]
    if gid not in gid2pieces:
      gid2pieces.update({gid:[]})
    gid2pieces[gid].append(piece)

  # get the correct mconnections and gconnections
  # Round-robin ranks that presently have the connection info for the gids
  rr = {}
  for gid in model.gids:
    r = gid%nhost
    if r not in rr:
      rr.update({r:[]})
    rr[r].append(gid);
  rr = all2all(rr)
  # rr is now the ranks for where to send the synapse information
  # all the gids in rr were 'owned' by the round-robin distribution
  # may wish to revisit so that only synapse info for relevant pieces is
  # scattered.
  
  mc = model.mconnections
  gc = model.rank_gconnections

  # construct a ggid2connection dict
  ggid2connection = {}
  for r in gc:
    for ci in gc[r]:
      ggid = ci[3]
      if ggid not in ggid2connection:
        ggid2connection.update({ggid:[]})
      ggid2connection[ggid].append(ci)
      
  for r in rr:
    gids = rr[r]
    mgci = []
    rr[r] = mgci
    for gid in gids:

      if gid in mc:
        mgci.append(mc[gid])
      elif gidfunc.isgranule(gid):
        mgci.append(ggid2connection[gid])
  mgci = all2all(rr)


  # mgci contains all the connection info needed by the balanced distribution
        
  # create mitrals and granules, split and register and create synapses
  nmc.dc.mk_mitrals(model) # whole cells 
  nmc.build_granules(model)
  nmc.build_blanes(model)
  
  for gid in gid2pieces:
    if ismitral(gid) or ismtufted(gid):
      split.splitmitral(gid, model.mitrals[gid], gid2pieces[gid])


  pc.multisplit()
  
  nmc.register_mitrals(model)
  nmc.register_granules(model)
  nmc.register_blanes(model)
  
  # build_synapses() ... use mgci to build explicitly
  model.mgrss = {}
  for r in mgci:
    for cil in mgci[r]:
      for ci in cil:
        if mgrs.mgrs_gid(ci[0], ci[3], ci[6]) not in model.mgrss:
          rsyn = mgrs.mk_mgrs(*ci[0:7])
          if rsyn:
            model.mgrss.update({rsyn.md_gid : rsyn})
  nmultiple = int(pc.allreduce(mgrs.multiple_cnt(), 1))


  # it is faster if generated again
  blanes.mk_gl2b_connections()
  # excitatory
  for mgid, blanes_gid, w in model.mt2blanes_connections:
    syn = blanes.mt2blanes(mgid, blanes_gid, w)
    model.mt2blanes[syn.gid] = syn

  blanes.mk_b2g_connections()
  # inhibitory synapses from blanes to gc
  for ggid, blanes_gid, w in model.blanes2gc_connections:
    syn = blanes.blanes2granule(blanes_gid, ggid, w)
    model.blanes2gc[syn.gid] = syn
        
  if rank == 0:
    print('nmultiple = ', nmultiple)
  detectors = h.List("AmpaNmda")
  util.elapsed('%d ampanmda for reciprocalsynapses constructed'%int(pc.allreduce(detectors.count(),1)))
  detectors = h.List("FastInhib")
  util.elapsed('%d fi for reciprocalsynapses constructed'%int(pc.allreduce(detectors.count(),1)))
  detectors = h.List("ThreshDetect")
  util.elapsed('%d ThreshDetect for reciprocalsynapses constructed'%int(pc.allreduce(detectors.count(),1)))
  util.elapsed('%d mt to bc' % int(pc.allreduce(len(model.mt2blanes),1)))
  util.elapsed('%d bc to gc' % int(pc.allreduce(len(model.blanes2gc),1)))

  if rank == 0: print('multisplit_distrib time ', h.startsw() - enter)

 
