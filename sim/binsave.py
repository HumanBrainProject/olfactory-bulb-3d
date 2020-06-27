
from util import *

def sort(t, g):
    # sort by gid
    gs = h.Vector()
    gs.copy(g)
    srt = gs.sortindex()
    gs.index(gs, srt)
    
    # sort the times
    ts = h.Vector()
    ts.copy(t)
    ts.index(ts, srt)
    
    # mk header
    header = []
    for i in range(int(gs.size())):
        gid = int(gs.x[i])
        
        if len(header) == 0 or gid != header[-1][0]:
            header.append([ gid, 1 ])
        else:
            header[-1][-1] += 1
            
    return ts, gs, header

def save(prefix, t, g):
    # sort
    ts, gs, header = sort(t, g)
    
    from struct import pack

    # write time
    if rank == 0:
        from neuron import h
        ft = open(prefix + '.time', 'wb')
        ft.write(pack('>f', h.t))
        ft.close()



    ngroup = nhost / max(nhost / 64, 1)
    for rg, rp in group_serialize(ngroup):
        
        fname_data = '%s.sbg.%04d' % (prefix, rg)
        fname_header = '%s.sbgh.%04d' % (prefix, rg)
        fname_dict = '%s.dic.%02d' % (prefix, rg)
        
        if rp:
            fd = open(fname_data, 'ab')
            fh = open(fname_header, 'ab')
            fdic = open(fname_dict, 'ab')
        else:
            fd = open(fname_data, 'wb')
            fh = open(fname_header, 'wb')
            fdic = open(fname_dict, 'wb')

        # output data
        for i in range(int(ts.size())):
            fd.write(pack('>f', ts.x[i]))

        # output header
        for gid, h in header:
            fh.write(pack('>LL', gid, h))

        # output dictionary
        for syn in getmodel().mgrss.values():
            if syn.md:
                fdic.write(pack('>LLHfLf', syn.md_gid, syn.mgid, syn.isec, syn.xm, syn.ggid, syn.xg))
            
        fd.close()
        fh.close()
        fdic.close()
#        binsave_calls += 1
                    
    

    

    

    

    
