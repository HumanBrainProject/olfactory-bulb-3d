from common import *
h('proc init() { local x       \n' + \
  '      finitialize(-55)  \n' + \
  '      fcurrent()     \n' + \
  '      forall {       \n' + \
  '            for(x) if(ismembrane("nax")) { \n' + \
  '                  e_pas(x) = -55 + (ina(x) + ik(x)) / g_pas(x) \n' + \
  '            }        \n' + \
  '      }              \n' + \
  '}                    \n')
import util
import parrun
import weightsave
import vrecord as vr
import net_mitral_centric as nmc
from odorstim import OdorStim
import gapjunc
def build_complete_model(dicfile=''):
  build_part_model(range(params.Ngloms), [], dicfile)
  
def build_part_model(gloms, mitrals, dicfile=''):

  model = getmodel()
  model.clear()

  # gids
  gids = set()
  for glomid in gloms:
    gids.update(range(glomid * params.Nmitral_per_glom, (glomid+1) * params.Nmitral_per_glom) + \
                range(glomid * params.Nmtufted_per_glom + params.gid_mtufted_begin, (glomid+1) * params.Nmtufted_per_glom + params.gid_mtufted_begin))
  gids.update(mitrals)
  
  # distribute
  nmc.build_net_round_robin(model, gids, dicfile)


  import distribute
  if False:
    # CoreNEURON does not support multisplit
    import multisplit_distrib
    multisplit_distrib.multisplit_distrib(distribute.getmodel())

  if params.gap_junctions_active:
    gapjunc.init() 


  # set initial weights
  if len(params.initial_weights) > 0:
    weightsave.weight_load(params.initial_weights)


  # print sections
  nc = h.List("NetCon")
  nc = int(pc.allreduce(nc.count(),1))
  if rank == 0: print "NetCon count = ", nc
  nseg = 0
  for sec in h.allsec():
    nseg += sec.nseg
  nseg = int(pc.allreduce(nseg, 1))
  if rank == 0: print "Total # compartments = ", nseg

  pc.spike_record(-1, parrun.spikevec, parrun.idvec)
  util.show_progress(200)


  odseq = [ OdorStim(*od) for od in params.odor_sequence ]
  model.odseq = odseq

  # record
  for rec in params.sec2rec:
    vr.record(*rec)


  if rank == 0: print 'total setup time ', h.startsw()-startsw



def run():
  
  parrun.prun(params.tstop)
  weightsave.weight_file(params.filename + '.weight.dat')
  vr.output()
  util.finish()
