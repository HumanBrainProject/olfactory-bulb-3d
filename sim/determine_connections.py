'''
Load balance requires an at present unknown gid distribution that cannot
be calculated til the connections are known. In particular, the complexity
of granules are dominated by their number of MGRS.
Calculation of all the connections and complexities can be accomplished
in parallel if we temporarily use a whole cell gid distribution in which
rank is easily derivable from gid, e.g. rank = gid%nhost. Then it is easy
to communicate the information needed to each rank.
'''

import params
granules = params.granules
from common import *
from all2all import all2all
import util
from gidfunc import *
import mkmitral

t_begin = h.startsw()

def gid2rank(gid):
  return gid%nhost


import lateral_connections as latconn



gc2nconn = {}
for ggid in list(granules.ggid2pos.keys()):
  if (ggid - params.gid_granule_begin) % nhost == rank:
    gc2nconn[ggid] = 0
  
def gid2rank(gid):
  return gid%nhost
    
# return which ranks has splitted the cells
def glom2ranks(glomid):
  return set([ mgid%nhost for mgid in range(glomid*params.Nmitral_per_glom, (glomid+1)*params.Nmitral_per_glom) ] + \
         [ mtgid%nhost for mtgid in range(glomid*params.Nmtufted_per_glom+params.gid_mtufted_begin, (glomid+1)*params.Nmtufted_per_glom+params.gid_mtufted_begin) ])

def ggid2rank(ggid):
  return (ggid - params.gid_granule_begin) % nhost

# ----------------------------------------------------------------------------------------------
# connect a segment to the granule
def connect2gc(cilist, r, gl2gc):
  for i in range(len(cilist)):
    gid = cilist[i][0]
    glomid = mgid2glom(gid) #params.cellid2glomid(gid)
    gcset = gl2gc[glomid]
    try:
      ggid, gisec, gx, gpos = latconn.connect_to_granule(cilist[i], r[gid], gcset)
      cilist[i] = cilist[i][:3]+(ggid, gisec, gx)+(cilist[i][-1],)
      gcset.add(gpos)
    except TypeError:
      cilist[i] = None

# find for intraglomerular connections
def detect_intraglom_conn(cilist, GL_to_GCs):
  # build message
  msg = {}
  for rr in range(nhost): msg[rr] = []
  for ci in cilist:
    if ci:
      glomid = mgid2glom(ci[0]) #params.cellid2glomid(ci[0])
      for rr in glom2ranks(glomid): # ranks to inform are only those > current rank
        if rr == rank:
          continue
        msg[rr].append((glomid, ci[3])) # information must be exchanged
  msg = all2all(msg) # exchange the new conn.
  
  # merge all connections
  tocheck = set()
  for rr, connpair in list(msg.items()):
    if rr >= rank:
      tocheck.update(connpair)
      
    # update connectivity info
    for glomid, ggid in connpair:
      try:
        GL_to_GCs[glomid].add(granules.ggid2pos[ggid])
      except KeyError:
        pass

    
  # distinguish between well vs already existing
  good_pair = []
  bad_pair = []
  for ci in cilist:
    if ci:
      if (mgid2glom(ci[0]), ci[3]) in tocheck:
        bad_pair.append(ci)
      else:
        good_pair.append(ci)
      
  return good_pair, bad_pair

# find for intraglomerular connections
def detect_over_connected_gc(_cilist):

  # granule cells new connections
  msg = {}
  ggid2ci = {}
  
  for _ci in _cilist:
    ggid = _ci[3]
    try:
      msg[ggid2rank(ggid)].append(_ci[3])
    except KeyError:
      msg[ggid2rank(ggid)] = [ _ci[3] ]
      
    try:
      ggid2ci[ggid].append(_ci)
    except KeyError:
      ggid2ci[ggid] = [ _ci ]
      
  msg = all2all(msg)
  
  # check for the over connected
  msg_remove = {}
  for rr, ggids in list(msg.items()):
    for ggid in ggids:
      if gc2nconn[ggid] >= params.granule_nmax_spines:
        try:
          msg_remove[rr].append(ggid)
        except KeyError:
          msg_remove[rr] = [ ggid ]
      else:
        gc2nconn[ggid] += 1

  msg_remove = all2all(msg_remove)

  # return
  good_pair = []
  bad_pair = []
  
  for ggids in list(msg_remove.values()):
    for ggid in ggids:
      bad_pair.append(ggid2ci[ggid][0])
      del ggid2ci[ggid][0]

  for _cilist2 in list(ggid2ci.values()):
    for ci in _cilist2:
      good_pair.append(ci)
      
  return good_pair, bad_pair
  

''' generate the connections for mitral and tufted cells '''
def mk_mconnection_info(model):
  r = {}
  GL_to_GCs = {}
  to_conn = []
  cilist = []

  # initialization
  for gid in list(model.mitrals.keys()): #+model.mtufted.keys():
    r[gid] = params.ranstream(gid, params.stream_latdendconnect) # init rng
    
    glomid = mgid2glom(gid) #params.cellid2glomid(gid) # init GCs connected to GL
    if glomid not in GL_to_GCs:
      GL_to_GCs[glomid] = set() 


  # lateral dendrites positions
  for cellid, cell in list(model.mitrals.items()): #+model.mtufted.values():
    to_conn += latconn.lateral_connections(cellid, cell)


  ntot_conn = pc.allreduce(len(to_conn),1) # all connections
  
  # connect to granule cells
  it = 0
  while pc.allreduce(len(to_conn), 2) > 0:
    connect2gc(to_conn, r, GL_to_GCs)
    # good connect vs to redo and update GL_to_GCs
    _cilist, to_conn1 = detect_intraglom_conn(to_conn, GL_to_GCs)
    #_cilist, to_conn2 = detect_over_connected_gc(_cilist)
    #to_conn = to_conn1 + to_conn2
    to_conn = to_conn1
    cilist += _cilist
    it += 1

  ntot_conn = pc.allreduce(len(cilist),1)/ntot_conn
  
  # fill the model data
  MCconn = 0
  mTCconn = 0
  for ci in cilist:
    #if params.gid_is_mitral(ci[0]):
    conns = model.mconnections
    MCconn += 1
    #elif params.gid_is_mtufted(ci[0]):
    #  conns = model.mt_connections
    #  mTCconn += 1
      
    if ci[0] not in conns:
      conns[ci[0]] = []
    conns[ci[0]].append(ci)
    
      
  util.elapsed('Mitral %d and mTufted %d cells connection infos. generated (it=%d,err=%.3g%%)'%(int(pc.allreduce(MCconn,1)),\
                                                                                                       int(pc.allreduce(mTCconn,1)),\
                                                                                                       int(pc.allreduce(it,2)),\
                                                                                                       (1-ntot_conn)*100))


#set of gids on this rank (default round-robin)
def round_robin_distrib(model):
  model.gids = set(range(rank, ncell, nhost))
  model.mitral_gids = set(range(rank, nmitral, nhost))
  model.granule_gids = model.gids - model.mitral_gids

round_robin_distrib(getmodel())

'''
In this section, presume connections determined by m2g_connections.py.
I.e. mitral statistics controlled and cause unknown granule statistics.
'''


def mk_mitrals(model):
  ''' Create all the mitrals specified by mitral_gids set.'''
  model.mitrals = {}
  for gid in model.mitral_gids:
    m = mkmitral.mkmitral(gid)
    model.mitrals[gid] = m
  util.elapsed('%d mitrals created and connections to mitrals determined'%int(pc.allreduce(len(model.mitrals),1)))

def mk_gconnection_info_part1(model):
  ''' after mk_gconnection_info_part2()
      rank_gconnections is the connection info for granules on rank ggid%nhost
      also granule_gids are the granules on this rank (granules with no
      connection will not exist)
  '''
  model.rank_gconnections = {}
  for cilist in list(model.mconnections.values()):
    for ci in cilist:
      ggid = ci[3]
      r = gid2rank(ggid)
      if r not in model.rank_gconnections:
        model.rank_gconnections[r] = []
      model.rank_gconnections[r].append(ci)

def mk_gconnection_info_part2(model):
  #transfer the gconnection info to the proper rank and make granule_gids set
  model.rank_gconnections = all2all(model.rank_gconnections)
  util.elapsed('rank_gconnections known')
  model.granule_gids = set([i[3] for r in model.rank_gconnections for i in model.rank_gconnections[r]])
  util.elapsed('granule gids known on each rank')

def mk_gconnection_info(model):
  mk_gconnection_info_part1(model)
  mk_gconnection_info_part2(model)
  util.elapsed('mk_gconnection_info (#granules = %d)'%int(pc.allreduce(len(model.granule_gids),1)))


if __name__ == '__main__':
  model = getmodel()
  mk_mitrals(model)
  mk_mconnection_info(model)
  mk_gconnection_info_part1(model)

  sizes = all2all(model.rank_gconnections, -1)
  for r in util.serialize():
    print(rank, " all2all sizes ", sizes)

if rank == 0: print("determine_connections ", h.startsw()-t_begin)

