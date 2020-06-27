

ggid2pos = {}
pos2ggid = {}

def init(center, upbnd, dwbnd, d, gid_granule_begin):
  # make a list of available granule cells
  from misc import Ellipsoid
  from math import exp
  
  ggid2pos.clear()
  pos2ggid.clear()
  up = Ellipsoid(center, upbnd)
  dw = Ellipsoid(center, dwbnd)
  
  gindex = 0
  for x in range(int((center[0]-upbnd[0]/2)/d)*d-d, int((center[0]+upbnd[0]/2)/d)*d+d+d, d):
    for y in range(int((center[1]-upbnd[1]/2)/d)*d-d, int((center[1]+upbnd[1]/2)/d)*d+d+d, d):
      for z in range(int((center[2]-upbnd[2]/2)/d)*d-d, int((center[2]+upbnd[2]/2)/d)*d+d+d, d):
        
        p =(x, y, z)
        if up.normalRadius(p) < 1.0 and dw.normalRadius(p) >= 1.0: # inside boundaries
          ggid = gid_granule_begin+gindex
              
          ggid2pos.update({ ggid:p })
          pos2ggid.update({ p:ggid })
          
          gindex += 1


if __name__ == '__main__':
  from common import rank
  if rank == 0:
    import params
    with open('../vis/granules.txt', 'w') as fo:
      for gid, p in params.granules.ggid2pos.items():
        fo.write('%d %d %d %d 0\n'%((gid,)+p))
