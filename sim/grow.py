# -*- coding: cp1252 -*-
import params
from gidfunc import *

import params

from math import sqrt, sin, cos, pi, exp, log

from misc import Ellipsoid, versor, getP, centroid, convert_direction, Spherical

from params import ranstream, stream_soma, stream_dend, stream_apic, stream_tuft
from params import glomRealCoords as glomCoord, bulbCenter, bulbAxis, GLOM_RADIUS
from misc import distance


# laplace rng
def rng_laplace(rng, mu, b, minval, maxval):
  
  def calcp(x):
    if x < mu:
      return 0.5*exp((x-mu)/b)
    return 1-0.5*exp(-(x-mu)/b)
  

  p = rng.uniform(calcp(minval), calcp(maxval))
  if p > 0.5:
    return -log((1-p)*2)*b+mu
  return log(p*2)*b+mu


def stretchSection(sec, p):
    dx = (sec[-1][0] - p[0]) / (len(sec) - 1)
    dy = (sec[-1][1] - p[1]) / (len(sec) - 1)
    dz = (sec[-1][2] - p[2]) / (len(sec) - 1)
    for k in range(1, len(sec)):
        sec[k][0] -= k * dx
        sec[k][1] -= k * dy
        sec[k][2] -= k * dz




class Section:
  def __init__(self):
    self.points = []
    self.children = []
    self.parent = None

  def connect(self, parent):
    if parent:
      self.parent = parent
      parent.children.append(self)
      self.points.append(parent.points[-1])
#      self.points[-1][-1] *= 0.5 ** (1/1.5)    
                
class Neuron:
  def __init__(self):
    self.dend = []
    self.apic = []
    self.tuft = []
    self.soma = []
    
class Extreme:
  SOMA = -1
  DENDRITE = 0
  APICAL = 1
  TUFT = 2

  def __init__(self):
    self.sec = None
    self.phi = 0.
    self.theta = 0.
    self.dist = 0.
    self.limit = 0.
    self.extr_type = Extreme.SOMA
    self.can_bifurc = False
    self.bif_dist = 0.
    self.bif_limit = 0.
    self.depth = 0
    self.basePhi = 0.
    self.baseTheta = 0.
                

  def diam(self):
    if self.extr_type == Extreme.APICAL:
      diam = self.cfg.APIC_DIAM
    elif self.extr_type == Extreme.TUFT:
      diam = self.cfg.TUFT_DIAM
    else:
      diam = self.sec.points[-1][-1] * exp(-self.cfg.diam_tape_dend*self.cfg.GRW_WALK_LEN)
    return diam
  

  def __update(self, p):
    d = distance(p, self.sec.points[-1][:3])
    self.dist += d
    self.bif_dist += d
    self.sec.points.append(p)
    
    
  def canDelete(self):  
    return self.extr_type != Extreme.APICAL and self.dist > self.limit and not self.can_bifurc
  
  
  def canBifurcate(self):
    return (self.extr_type == Extreme.DENDRITE and self.can_bifurc and self.bif_dist > self.bif_limit) or \
           (self.extr_type == Extreme.APICAL and self.dist > self.limit) 


  def grow(self):
    r = self.r[self.extr_type]

    if self.extr_type == Extreme.APICAL:
      def bias(): pass
    elif self.extr_type == Extreme.TUFT:
      def bias():
        _phi, _theta = convert_direction(self.phi, self.theta, self.basePhi, self.baseTheta)
        p = Spherical.xyz(self.cfg.GRW_WALK_LEN, _phi, _theta, self.sec.points[-1][:3])
        dglom = distance(p, self.glomPos)
        if dglom > GLOM_RADIUS * 0.9:
          _phi, _theta = Spherical.to(getP(dglom-GLOM_RADIUS*0.9, versor(self.glomPos, p), p), self.sec.points[-1][:3])[1:]
          self.phi, self.theta = convert_direction(_phi, _theta, self.basePhi, self.baseTheta, True)
    else:
          
      def EllipsoidPression(p, axis, up, k):
        e = Ellipsoid(bulbCenter, axis)
        h = e.normalRadius(p)

        q = None
        
        _lamb, _phi = e.toElliptical(p)[1:]
        F = h * k
        q = [ -F * sin(_lamb) * cos(_phi) + p[0], -F * cos(_lamb) * cos(_phi) + p[1], -F * sin(_phi) + p[2] ]
                
        vNew = versor(q, self.sec.points[-1][:3])
        _p = getP(self.cfg.GRW_WALK_LEN, vNew, self.sec.points[-1][:3])
        _phi, _theta = Spherical.to(_p, self.sec.points[-1][:3])[1:]
        return _p, _phi, _theta


      def bias():
        e = Ellipsoid(bulbCenter, bulbAxis)
        
        _phi, _theta = convert_direction(self.phi, self.theta, self.basePhi, self.baseTheta)
        p = Spherical.xyz(self.cfg.GRW_WALK_LEN, _phi, _theta, self.sec.points[-1][:3])

        if e.normalRadius(self.sec.points[-1][:3]) < e.normalRadius(p):
          p, _phi, _theta = EllipsoidPression(p, bulbAxis, True, self.cfg.GROW_RESISTANCE)
          self.phi, self.theta = convert_direction(_phi, _theta, self.basePhi, self.baseTheta, True)
      

    bias()
    _phi, _theta = convert_direction(self.phi, self.theta, self.basePhi, self.baseTheta)           
    _phi += rng_laplace(r, 0, self.cfg.NS_PHI_B, self.cfg.NS_PHI_MIN, self.cfg.NS_PHI_MAX)
    _theta += rng_laplace(r, 0, self.cfg.NS_THETA_B, self.cfg.NS_THETA_MIN, self.cfg.NS_THETA_MAX)
    p = Spherical.xyz(self.cfg.GRW_WALK_LEN, _phi, _theta, self.sec.points[-1][:3]) + [self.diam()]
    self.__update(p)


  # change extremity, especially at the end of apical                                                             
  def Bifurcate(self):
    r = self.r[self.extr_type]
    _extrLs = []
    
    if self.extr_type == Extreme.APICAL:

      if distance(self.sec.points[-1][:3], self.glomPos) != GLOM_RADIUS:
        pos = getP(distance(self.sec.points[-1][:3], self.glomPos)-GLOM_RADIUS,
                   versor(self.glomPos, self.sec.points[-1][:3]),
                   self.sec.points[-1][:3])
        stretchSection(self.sec.points, pos)
      # orientation respect glomerulus
      gl_phi, gl_theta = Spherical.to(self.glomPos, self.sec.points[-1][:3])[1:]
      
      # make tuft        
      TUFTS = int(r.discunif(self.cfg.N_MIN_TUFT, self.cfg.N_MAX_TUFT))
      for i in range(TUFTS):
        sec = Section()
        sec.connect(self.nrn.apic[0])
        self.nrn.tuft.append(sec)
        extr = Extreme()
        extr.sec = sec
        extr.phi, extr.theta = i * 2 * pi / TUFTS * (1 + 0.75 * r.uniform(-0.5 / TUFTS, 0.5 / TUFTS)), pi / 4
        extr.basePhi, extr.baseTheta = self.basePhi, self.baseTheta
        extr.limit = r.uniform(self.cfg.TUFT_MIN_LEN, self.cfg.TUFT_MAX_LEN)
        extr.extr_type = Extreme.TUFT
        extr.glomPos = self.glomPos

        extr.cfg = self.cfg
        extr.r = self.r
        extr.nrn = self.nrn
        
        _extrLs.append(extr)
          
    elif self.extr_type == Extreme.DENDRITE:

      
      def get_phi():
        phi = r.negexp(self.cfg.BIFURC_PHI_MU)
        while phi < self.cfg.BIFURC_PHI_MIN or phi > self.cfg.BIFURC_PHI_MAX:
          phi = r.repick()
        return phi

      for i in range(2):
        sec, extr = mkDendrite(self.cfg, self.r, self.nrn, self.depth + 1, self.sec)

        self.nrn.dend.append(sec)
      
        extr.phi = self.phi + ((-1) ** i) * get_phi()
        extr.theta = self.theta
        extr.dist = self.dist
        extr.basePhi = self.basePhi
        extr.baseTheta = self.baseTheta
        _extrLs.append(extr)


    return _extrLs




def gen_soma_pos(cfg, rng_sm, glompos, gid):
  upbnd = Ellipsoid(params.bulbCenter, cfg.somaAxisUp)
  dwbnd = Ellipsoid(params.bulbCenter, cfg.somaAxisDw)
  if ismitral(gid):
    import mcgrow
    ncell_per_glom = params.Nmitral_per_glom
  else:
    import mtgrow
    ncell_per_glom = params.Nmtufted_per_glom
    
  glpj_up = upbnd.project(glompos)
  somapos=glpj_up
  base_phi, base_theta = upbnd.toElliptical(glompos)[1:]
  base_phi = pi/2-base_phi; base_theta = pi/2-base_theta
  
  radius = rng_sm.uniform(cfg.GLOM_DIST, cfg.GLOM_DIST)
  phi = (gid%ncell_per_glom)*2*pi/ncell_per_glom + \
        params.ranstream(mgid2glom(gid), stream_soma).uniform(0, 2*pi)
  
  theta = pi/2
  absphi, abstheta = convert_direction(phi, theta, base_phi, base_theta)
  p = Spherical.xyz(radius, absphi, abstheta, glpj_up)
  p_up = upbnd.project(p)
  p_dw = dwbnd.project(p)
  x = rng_sm.uniform(0, 1)
  somapos = [x*(p_up[0]-p_dw[0])+p_dw[0], x*(p_up[1]-p_dw[1])+p_dw[1], x*(p_up[2]-p_dw[2])+p_dw[2]]
  
  return somapos #, base_phi, base_theta



def mk_soma(cfg, r, mgid, nrn):
  sec = Section()
  glompos = glomCoord[mgid2glom(mgid)]
  somapos = gen_soma_pos(cfg, r, glompos, mgid)

  sec.points = cfg.realSoma.realSoma(int(r.discunif(0, cfg.realSoma.N_SOMA-1)), somapos)
  nrn.soma.append(sec)

  return somapos

def mk_apic(cfg, somaPos, nrn):
  sec = Section()
  sec.points = [ somaPos+[cfg.APIC_DIAM] ]
  sec.connect(nrn.soma[0])
  nrn.apic.append(sec)
                                                                                     

        
def mkDendrite(cfg, _r, nrn, depth, parent):
        r = _r[Extreme.DENDRITE]
        sec = Section()
        sec.connect(parent)
        
        extr = Extreme()
        extr.extr_type = Extreme.DENDRITE
        extr.sec = sec
        
        # bifurcation decision
        extr.can_bifurc = depth < len(cfg.branch_prob) and r.uniform(0, 1) <= cfg.branch_prob[depth] and extr.dist < (cfg.DEND_LEN_MAX - cfg.DEND_LEN_MIN)
        extr.depth = depth

        if extr.can_bifurc:
          min_len = cfg.branch_len_min[depth]
          max_len = cfg.branch_len_max[depth]          
          L = r.negexp(cfg.branch_len_mean[depth])
          while L < min_len or L > max_len:
            L = r.repick()
          extr.bif_limit = L
          
        else:
          min_len = cfg.DEND_LEN_MIN + extr.dist
          max_len = cfg.DEND_LEN_MAX          
          L = r.normal(cfg.DEND_LEN_MU, cfg.DEND_LEN_VAR)
          while L < min_len or L > max_len:
            L = r.repick()
          extr.limit = L

        extr.cfg = cfg
        extr.r = _r
        extr.nrn = nrn               
        return sec, extr




# initialization of algorithm
def initGrow(cfg, mid):
  nrn = Neuron()
  extrLs = [ ]
  
  r = [ 
        ranstream(mid, stream_dend), \
        ranstream(mid, stream_apic), \
        ranstream(mid, stream_tuft) ]


  glomPos = glomCoord[mgid2glom(mid)]
  somaPos = mk_soma(cfg, ranstream(mid, stream_soma), mid, nrn) # initialize the 


  mk_apic(cfg, somaPos, nrn)
  


  
  somaLvl = Ellipsoid(bulbCenter, cfg.somaAxisDw)
  phi_base, theta_base = somaLvl.toElliptical(somaPos)[1:]
  theta_base = pi / 2 - theta_base
  phi_base = pi / 2 - phi_base


  extr = Extreme()
  extr.cfg = cfg
  extr.r = r
  extr.nrn = nrn
  extr.glomPos = glomPos
  extr.sec = nrn.apic[0]
  
  extr.phi, extr.theta = Spherical.to(glomPos, somaPos)[1:]
  extr.phi, extr.theta = convert_direction(extr.phi, extr.theta, phi_base, theta_base, True)
  extr.extr_type = Extreme.APICAL
  extr.limit = cfg.APIC_LEN_MAX
  extr.basePhi = phi_base
  extr.baseTheta = theta_base
  
  extrLs.append(extr)
  
  
  rd = r[Extreme.DENDRITE]


  #if ismitral(mid):
  DENDRITES = int(rd.negexp(cfg.N_MEAN_DEND - cfg.N_MIN_DEND)) + cfg.N_MIN_DEND
  while DENDRITES > cfg.N_MAX_DEND:
    DENDRITES = int(rd.repick()) + cfg.N_MIN_DEND
  #else:
  #DENDRITES = int(rd.negexp(cfg.N_MEAN_DEND)) 
  #while DENDRITES < cfg.N_MIN_DEND or DENDRITES > cfg.N_MAX_DEND:
  #  DENDRITES = int(rd.repick())

  if ismitral(mid):
    ncell_per_glom = params.Nmitral_per_glom
    cell_index = (mid - params.gid_mitral_begin) % ncell_per_glom
  elif ismtufted(mid):
    ncell_per_glom = params.Nmtufted_per_glom
    cell_index = (mid - params.gid_mtufted_begin) % ncell_per_glom
    
    
  phi_phase = 2 * pi / cfg.N_MEAN_DEND / ncell_per_glom * cell_index 
  
  for i in range(DENDRITES):
           
    sec, extr = mkDendrite(cfg, r, nrn, 0, nrn.soma[0])
    sec.points = [ somaPos + [ rd.uniform(cfg.diam_min_dend, cfg.diam_min_dend) ] ]      
    nrn.dend.append(sec)
    extr.phi = 2 * pi / DENDRITES * i + phi_phase
    extr.theta = cfg.init_theta                
    extr.basePhi = phi_base
    extr.baseTheta = theta_base
    extrLs.append(extr)

  return nrn, extrLs


def Grow(cfg, mid):
  nrn, extrLs = initGrow(cfg, mid)       

  for it in range(cfg.GROW_MAX_ITERATIONS):

    if len(extrLs) == 0:
      break

    _extrLs = []

    for e in extrLs:
      e.grow()
                     
      if e.canDelete():
        continue       
      elif e.canBifurcate():
        _extrLs += e.Bifurcate()
      else:
        _extrLs.append(e)

    extrLs = _extrLs

  
  return nrn

def genMitral(mid):
  import mcgrow
  return Grow(mcgrow, mid)

def genMTufted(mid):
  import mtgrow
  return Grow(mtgrow, mid)

