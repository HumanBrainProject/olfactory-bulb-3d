from common import *
import params

class dSAC:
  def __init__(self, gid, spine):
    self.rng = params.ranstream(gid, params.stream_dsac)
    self.rng.negexp(1)
    
    self.spine = spine
    
    self.gaba = h.FastInhib(self.spine.neck(0.5))
    self.gaba.training = 0
    self.gaba.gmax = params.dsac_gmax
    
    self.stim = h.NetStim(0.5)
    self.stim.start = 0
    self.stim.number = 1e+9
    self.stim.noise = 1.0
    self.stim.interval = 1.0 / (17.0 / 1000)
    self.stim.noiseFromRandom(self.rng)

    self.nc = h.NetCon(self.stim, self.gaba)
    self.nc.delay = 1
    self.nc.weight[0] = 1
    self.nc.weight[1] = 50

  def set_stim(self, intens):
    pass
