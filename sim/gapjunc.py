
    
import split
from neuron import h
import params; nmxg = params.Nmitral_per_glom; nmt = params.Nmtufted_per_glom; nmi = params.gid_mtufted_begin
from common import pc, getmodel, nhost
import util
import all2all as a2a
h.load_file('gj_nrn.hoc')
from gidfunc import ismitral, ismtufted, mgid2glom

gj_min_g1=0
gj_max_g1=2.5
gj_min_g3=0
gj_max_g3=2.5
gj_min_g2=0
gj_max_g2=0.001

def init():
    data = {}
    for uid in range(nhost):
      data.update({ uid:(list(getmodel().mitrals.keys())) })
    data = a2a.all2all(data)
    mgids = []
    for _mgids in list(data.values()): mgids += _mgids
    mgids = set(mgids)

    # initialize source
    
    for mgid in list(getmodel().mitrals.keys()):
        mpriden = split.mpriden(mgid)
        if not mpriden:
          continue
       
        rgj = params.ranstream(mgid, params.stream_gap_junction)

        
        mpriden.push()
        secref = h.SectionRef()
        h.pop_section()
        
        h.mk_gj_src(pc, mgid, secref)

        glomid = mgid2glom(mgid)
        
        sistergids = []

        # no longer all to all, only a chain
        if not (ismtufted(mgid) and (mgid - nmi) % nmt == (nmt - 1)):
            if ismitral(mgid) and mgid % nmxg == (nmxg - 1):
                sistergids += [glomid * nmt + nmi]
            else:
                sistergids += [mgid + 1]
            
        if not (ismitral(mgid) and mgid % nmxg == 0):
            if ismtufted(mgid) and (mgid - nmi) % nmt == 0:
                sistergids += [(glomid + 1) * nmxg - 1]
            else:
                sistergids += [mgid - 1]
            
        sistergids = mgids.intersection(list(range(glomid * nmxg, glomid * nmxg + nmxg)) + list(range(glomid * nmt + nmi, glomid * nmt + nmt + nmi))).difference([ mgid ])  

        for sistermgid in sistergids:
            gap = h.Gap(mpriden(0.99))

            if ismitral(mgid) and ismitral(sistermgid):
                gap.g = rgj.uniform(gj_min_g1, gj_max_g1)
            elif  ismtufted(mgid) and ismtufted(sistermgid):
                gap.g = rgj.uniform(gj_min_g3, gj_max_g3)
            else:
                gap.g = rgj.uniform(gj_min_g2, gj_max_g2)
                

            getmodel().gj[(mgid, sistermgid)] = gap
            

    pc.barrier()

    # initialize targets
    for key, gap in list(getmodel().gj.items()):
        mgid, sistermgid = key
        pc.target_var(gap, gap._ref_vgap, sistermgid)

    util.elapsed('Gap junctions built')


