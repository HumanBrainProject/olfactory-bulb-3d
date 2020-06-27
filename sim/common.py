from neuron import h

startsw = h.startsw()
h.load_file("stdgui.hoc")

h("proc setdt(){}")
h.dt = 2*(1./64. + 1./128)

pc = h.ParallelContext()
rank = int(pc.id())
nhost = int(pc.nhost())

import params
nmitral = params.Nmitral
nmtufted = params.Nmtufted
ngranule = params.Ngranule
nblanes = params.NBlanes
ncell = nmitral + nmtufted + ngranule + nblanes

from modeldata import getmodel
