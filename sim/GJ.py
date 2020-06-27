
    
import split
from neuron import h
import params; nmxg = params.Nmitral_per_glom; nm = params.Nmitral
from common import pc, getmodel
import util


def init_gap_junctions():

    # initialize source
    for mgid in range(params.Nmitral):
        mpriden = split.mpriden(mgid)
        if mpriden:
            mpriden.push()
            pc.source_var(mpriden(0.99)._ref_v, mgid)
            h.pop_section()
            
    pc.barrier()

    # initialize targets
    for mgid in range(params.Nmitral):
        mpriden = split.mpriden(mgid)
        if mpriden:
            glomid = mgid/nmxg
            for sistermgid in range(glomid * nmxg, mgid)+range(mgid+1, (glomid+1)*nmxg):
                if pc.gid_exists(sistermgid) > 0:
                    gap = h.Gap(mpriden(0.99))
                    if sistermgid != 189:
                        getmodel().gj[(mgid, sistermgid)] = gap
                        glomid = mgid / nmxg
                        pc.target_var(gap, gap._ref_vgap, sistermgid)
    util.elapsed('Gap junctions builden')

def gap_junctions_cnt():
    return len(getmodel().gj)*2
