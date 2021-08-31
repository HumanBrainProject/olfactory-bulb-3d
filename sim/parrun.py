from common import *
h.load_file("spike2file.hoc")


idvec = h.Vector()
idvec.buffer_size(5000000)
spikevec = h.Vector()
spikevec.buffer_size(5000000)

n_spkout_files = max(nhost/64, 1) # each file contains spikes from 64 ranks
n_spkout_sort = min(n_spkout_files*8, nhost) #each file serializes from 8 ranks
# so each sorting rank gathers spikes from nhost/n_spkout_sort ranks
checkpoint_interval = 100000
clean_weights_active = False
clean_weights_interval = 10500.0

from weightsave import weight_reset as clean_weights, weight_file

def prun(tstop):
  isaved=0
  cvode = h.CVode()
  cvode.cache_efficient(1)
  #pc.spike_compress(0,0,1)
  pc.setup_transfer()
  #pc.timeout(0)
  mindelay = pc.set_maxstep(10)
  if rank == 0: print('mindelay = %g'%mindelay)

  cvode.active(0)
  h.stdinit()

  runtime = h.startsw()
  exchtime = pc.wait_time()
  solver_time = 0

  inittime = h.startsw()
  if rank == 0: print('cvode active=', cvode.active())

  if rank == 0:
    if clean_weights_active:
      print('weights reset active at %g ms' % clean_weights_interval)
    else:
      print('weights reset not active')

  tnext_clean = clean_weights_interval

  # if coreneuron is enabled, run it with coreneuron
  if params.coreneuron:
    from neuron import coreneuron
    coreneuron.enable = True
    coreneuron.filemode = params.filemode
    coreneuron.gpu = params.gpu
    if params.gpu:
      coreneuron.cell_permute = 2
      coreneuron.warp_balance = 2048
    pc.psolve(tstop)
    h.spike2file(params.filename, spikevec, idvec, n_spkout_sort, n_spkout_files)
  else:
    # neuron execution
    inittime = h.startsw() - inittime
    print('init time = %g'%inittime)

    while h.t < tstop:
      told = h.t
      tnext = h.t + checkpoint_interval

      if tnext > tstop:
        tnext = tstop

      #if clean_weights_active:
        #while tnext_clean < tnext:
          #pc.psolve(tnext_clean)
          #clean_weights()
          #tnext_clean += clean_weights_interval

      t = h.startsw()
      pc.psolve(tnext)
      solver_time += (h.startsw() - t)

      #if rank == 0:
        #print 'sim. checkpoint at %g' % h.t

      if h.t == told:
        if rank == 0:
          print("psolve did not advance time from t=%.20g to tnext=%.20g\n"%(h.t, tnext))
        break
      # weight_file(params.filename+('.%d'%isaved))
      # save spikes and dictionary in a binary format to
      # make them more comprimibles
      import binsave
      binsave.save(params.filename, spikevec, idvec)
      h.spike2file(params.filename, spikevec, idvec, n_spkout_sort, n_spkout_files)

  # for cmparison with CoreNEURON, print psolve time
  if rank == 0 and not params.coreneuron:
    print('Solver time : %g'% solver_time)
  
  runtime = h.startsw() - runtime
  comptime = pc.step_time()
  splittime = pc.vtransfer_time(1)
  gaptime = pc.vtransfer_time()
  exchtime = pc.wait_time() - exchtime
  if rank == 0: print('runtime = %g'% runtime)
  printperf([comptime, exchtime, splittime, gaptime])

def printperf(p):
  avgp = []
  maxp = []
  header = ['comp','spk','split','gap']
  for i in p:
    avgp.append(pc.allreduce(i, 1)/nhost)
    maxp.append(pc.allreduce(i, 2))
  if rank > 0:
    return
  b = avgp[0]/maxp[0]
  print('Load Balance = %g'% b)
  print('\n     ', end=' ')
  for i in header: print('%12s'%i, end=' ')
  print('\n avg ', end=' ')
  for i in avgp: print('%12.2f'%i, end=' ')
  print('\n max ', end=' ')
  for i in maxp: print('%12.2f'%i, end=' ')
  print('')
 
if __name__ == '__main__':
  import common
  import util
  common.nmitral = 1
  common.ncell = 2
  import net_mitral_centric as nmc
  nmc.build_net_roundrobin(getmodel())
  pc.spike_record(-1, spikevec, idvec)
  from odorstim import OdorStim
  from odors import odors
  ods = OdorStim(odors['Apple'])
  ods.setup(nmc.mitrals, 10., 20., 100.)
  prun(200.)
  util.finish()
