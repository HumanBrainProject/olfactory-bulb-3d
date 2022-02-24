import params
import runsim
import odors
import sys
from math import sqrt

params.sniff_invl_min = params.sniff_invl_max = 500
params.training_exc = params.training_inh = True

from neuron import h
h('sigslope_AmpaNmda=5')
h('sigslope_FastInhib=5')
h('sigexp_AmpaNmda=4')
params.odor_sequence = [ ('Onion', 50, 1000, 1e+9) ]
#runsim.build_part_model([5,37,32,78,7], [])
#runsim.build_part_model(range(0, 120), [])
#runsim.build_part_model([5,37,32,78,7,0,1,2,3,4,6,8], [])
runsim.build_part_model(range(0, 120), [])
runsim.run()
