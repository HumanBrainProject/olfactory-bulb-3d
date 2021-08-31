
# -*- coding: cp1252 -*-

# bulb spatial definition

bulbCenter = [ 50., 1275., 0. ]
bulbAxis = [ 2100., 2800., 2100.]
glomAxis = [ bulbAxis[i]+300 for i in range(3) ]
granAxisUp = [ bulbAxis[i]-700 for i in range(3) ]
granAxisDw = [ bulbAxis[i]-1500 for i in range(3) ]

GLOM_RADIUS = 50.

# coreneuron parameters
coreneuron = False
gpu = False
filemode = False

try:
    
    from neuron import h
    h.celsius = 35
    
except:
    pass


filename = 'cfg27'

def load_params(_filename):
    global filename
    global stream_last
    global stream_orn_w
    global stream_orn_act
    
    filename = _filename
    try:
      module = __import__(filename)
      globals().update(vars(module))
      stream_last = stream_last_fixed+stream_ods_shift
      stream_orn_w = stream_last; stream_last += 6
      stream_orn_act = stream_last; stream_last += 1
      glom2blanes = []
      with open('blanes_exc_conn.txt', 'r') as fi:
        l = fi.readline()
        while l:
          tk = l.split()
          glom2blanes.append((int(tk[0]), int(tk[1])))
          l = fi.readline()
    except:
      print('error during params import')

from copy import copy
from math import pi, sqrt

use_fi_stdp = False # FastInhibSTDP vs FastInhib


#plasticity
mc_fi_tau1 = 1
mc_fi_tau2 = 5

mt_fi_tau1 = 1
mt_fi_tau2 = 5

gran_voxel = 17  #19
gran_connect_radius = 41.
mean_synapse_invl = 10.0



glomRealCoords = []
with open('realgloms.txt', 'r') as fi:
    line = fi.readline()
    while line:
        token = line.split()
        glomRealCoords.append([ float(token[0]), float(token[1]), float(token[2]) ])
        line = fi.readline()


glomRealCoords = glomRealCoords[:127]
# cell numbers    
Ngloms = len(glomRealCoords) # glomeruli

# mitral
gid_mitral_begin = 0
Nmitral_per_glom = 5 # mitral per glomerolus
Nmitral = Ngloms * Nmitral_per_glom

# middle tufted
gid_mtufted_begin = gid_mitral_begin+Nmitral
Nmtufted_per_glom = 2*Nmitral_per_glom # twice than mitral!
Nmtufted = Ngloms * Nmtufted_per_glom

gid_granule_begin = gid_mtufted_begin + Nmtufted
import granules
granules.init(bulbCenter, granAxisUp, granAxisDw, gran_voxel, gid_granule_begin)
Ngranule = len(granules.ggid2pos)

gid_blanes_begin = gid_granule_begin+Ngranule
NBlanes_per_glom = 3
NBlanes = Ngloms*NBlanes_per_glom
gid_mbs_begin = gid_blanes_begin+NBlanes
gid_bc2gc_begin = gid_mbs_begin+Nmtufted*NBlanes

# reciprocal synapse
gid_mgrs_begin = gid_bc2gc_begin+NBlanes*Ngranule
if gid_mgrs_begin % 2 != 0:
  gid_mgrs_begin += 1

# Random123 secondary stream identifiers
# note: the primary stream index is the "gid" which is ordered as
# Nmitral, Ngranule, synapses
# Not all secondary identifiers are used for all types
stream_last=1
stream_soma = stream_last; stream_last += 1
stream_dend = stream_last; stream_last += 1
stream_apic = stream_last; stream_last += 1
stream_tuft = stream_last; stream_last += 1
stream_latdendconnect = stream_last; stream_last += 1000 #allows per dendrite stream
stream_dsac = stream_last; stream_last += Nmitral+Nmtufted
stream_granule_diam = stream_last; stream_last += 1
stream_granule_type = stream_last; stream_last += 1
stream_granule_dsac = stream_last; stream_last += 8
stream_gap_junction = stream_last; stream_last += 1
stream_blanes = stream_last+Ngranule+Nmtufted; stream_last += 1
stream_blanes_conn = stream_last+Ngranule; stream_last += 1
stream_last_fixed = stream_last

# for the odorstim
stream_last = stream_last_fixed
stream_orn_w = stream_last; stream_last += 6
stream_orn_act = stream_last; stream_last += 1
stream_sniff_delay = stream_last; stream_last += 1


granule_rn_mean = 603.2
granule_rn_std = 363.4/10.

#granule_rn_mean = 728.7
#granule_rn_std = 293.06/10


def ranstream(id1, id2):
    r = h.Random()
    r.Random123(id1, id2)
    return r




# learning
orn_g_mc_std = 1e-4
orn_g_mt_std = 1e-4


if False:
  orn_g_mc_baseline = 0
  orn_g_mc_max = 15e-3
  orn_g_mt_baseline = 0
  orn_g_mt_max = 15e-3
else:
  orn_g_mc_baseline = 5e-4
  orn_g_mc_max = 4e-3
  orn_g_mt_baseline = 5e-4
  orn_g_mt_max = 10e-3


scrambled_weights = False
gap_junctions_active = True
glomerular_layer = 2


load_params('cfg27')

gc_type3_prob=0

vclamp = []

