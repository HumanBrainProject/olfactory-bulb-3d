from neuron import h
import params
import misc
granules = params.granules
from gidfunc import *

# set granules type #

pos2type = {}
_gran_voxel = set([ (0, 0, 0) ])

def gc_is_superficial(ggid):  
  p = granules.ggid2pos[ggid]
  # it fix the granule cells type
  up = misc.Ellipsoid(params.bulbCenter, params.granAxisUp)
  dw = misc.Ellipsoid(params.bulbCenter, params.granAxisDw)
  return (dw.normalRadius(p)-1)/(dw.normalRadius(up.project(p))-1) > 0.5

def init():
  from math import exp
  
  # it fix the granule cells type
  up = misc.Ellipsoid(params.bulbCenter, params.granAxisUp)
  dw = misc.Ellipsoid(params.bulbCenter, params.granAxisDw)
  
  for p, ggid in granules.pos2ggid.items():
    
    rng_type = params.ranstream(ggid, params.stream_granule_type)
    if rng_type.uniform(0, 1) < params.gc_type3_prob:
#    if False:
      gtype = 1
    else:
      prob = (dw.normalRadius(p)-1)/(dw.normalRadius(up.project(p))-1)
      
      #if rng_type.uniform(0, 1) > prob:
      if prob <= 0.5:
#      if not gc_is_superficial(ggid):
        gtype = 0 # right type for mitral only
      else:
        gtype = 2 # right type for mid. tufted only 
    pos2type[p] = gtype
    
  
  # initialize the voxel grid to connect segment to granule cells
  d = params.gran_voxel
  ndepth = int(round(params.gran_connect_radius/d))
  old_moves = set([ (0, 0, 0) ])
  for idepth in range(ndepth):
    new_moves = set()
    for m in old_moves:
      for dx in range(-d, d+1, d):
        for dy in range(-d, d+1, d):
          for dz in range(-d, d+1, d):
            p = (m[0]+dx, m[1]+dy, m[2]+dz)
            new_moves.add(p)
            _gran_voxel.add(p)
    old_moves = new_moves


# ----------------- #


''' get the voxels below the segment would connect to '''
def get_granules_below(p, glomid):
  bnd_up = misc.Ellipsoid(params.bulbCenter, params.granAxisUp)
  bnd_dw = misc.Ellipsoid(params.bulbCenter, params.granAxisDw)
  
  p_up = bnd_up.project(p)
  p_dw = bnd_dw.project(p) #params.glomRealCoords[glomid])

  

  def get_neighbors(q):
    neighpt = []
    for dx, dy, dz in _gran_voxel:
      neighpt.append((q[0]+dx, q[1]+dy, q[2]+dz))
    return neighpt


  def get_p(x):
    d=params.gran_voxel
    return (int((p_dw[0]+x*(p_up[0]-p_dw[0]))/d)*d,
            int((p_dw[1]+x*(p_up[1]-p_dw[1]))/d)*d,
            int((p_dw[2]+x*(p_up[2]-p_dw[2]))/d)*d)
    

  pts = set()
  nmoves = 1+int(misc.distance(p_up, p_dw)/params.gran_voxel)
  x = 0.0
  while x < 1:
    pts.update(get_neighbors(get_p(x)))
    x += 1.0/nmoves
  return pts

''' dendrites locations to connect '''
def dend_connections(sec):
  sec.push()
  
  n = int(h.n3d())
  
  x = h.Vector(n)
  y = h.Vector(n)
  z = h.Vector(n)
  s = h.Vector(n)

  for i in range(n):
    x.x[i] = h.x3d(i)
    y.x[i] = h.y3d(i)
    z.x[i] = h.z3d(i)
    s.x[i] = h.arc3d(i)


  # find arc to interp
  s1 = h.Vector()
  arc = params.mean_synapse_invl/2
  while arc < sec.L:
    s1.append(arc)
    arc += params.mean_synapse_invl
  
  h.pop_section()


  # interpolate
  x.interpolate(s1, s)
  y.interpolate(s1, s)
  z.interpolate(s1, s)
  s1.mul(1.0/sec.L)
  
  return s1, x, y, z
  
    
''' cell lat. dend. locations to connect '''
def lateral_connections(cellid, cell):
  ci = []

  for i in range(int(cell.nsecden)):
    s, x, y, z = dend_connections(cell.secden[i])
    for j in range(int(s.size())):
      ci.append((int(cellid), i, s.x[j], None, 0, None, 
                 0, (x.x[j], y.x[j], z.x[j])))
  return ci


''' choice a granule to connect '''
def connect_to_granule(ci, rng, gconnected):
  up = misc.Ellipsoid(params.bulbCenter, params.granAxisUp)
  dw = misc.Ellipsoid(params.bulbCenter, params.granAxisDw)
  
  gvoxels = list(get_granules_below(ci[-1], mgid2glom(ci[0])))

  def inside_boundary(p):
    return up.normalRadius(p) < 1 and dw.normalRadius(p) >= 1
  
  def is_proper_type(cgid, gpos):
    gtype = pos2type[gpos]
    if ismitral(cgid):
      return gtype == 0 or gtype == 1
    elif ismtufted(cgid):
      return gtype == 1 or gtype == 2
    return False
      
  while True:
    # cannot connect
    if len(gvoxels) == 0:
      break
    
    index = int(rng.discunif(0, len(gvoxels)-1))
    gpos = gvoxels[index]

    # the voxel is a granule
    if inside_boundary(gpos) and gpos not in gconnected and is_proper_type(ci[0], gpos):
      return granules.pos2ggid[gpos], 0, rng.uniform(0, 1), gpos

    del gvoxels[index]
    
  return None





# initialize the lateral connections
init()
  
if __name__ == '__main__':

  def ggid2type_save(filename):
    with open(filename, 'w') as fo:
      for gpos, gtype in pos2type.items():
        fo.write('%d %d\n' % (granules.pos2ggid[gpos], \
                            gtype) \
                 )

  ggid2type_save('../bulbvis/ggid2type.txt')

  with open('../bulbvis/granules.txt', 'w') as fo:
    for ggid, p in granules.ggid2pos.items():
      fo.write('%d ' % ggid)
      fo.write('%g %g %g '% p)
      fo.write('%d\n' % 0)
  n = [0]*3
  for gtype in pos2type.values(): n[gtype]+=1
  print n
  print 'saved'
