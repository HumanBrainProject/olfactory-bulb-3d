
import params
import misc
from math import pi 

# 3d coords to ellipsoidal
def p2e(p, axis=params.bulbAxis):
  from copy import copy  
  p = copy(p)
  for i in range(3):
    p[i] -= params.bulbCenter[i]
    p[i] /= axis[i] / 2.0
  phi, theta = misc.Spherical.to(p)[1:]
  phi %= 2*pi
  return phi, theta

def e2p(phi, theta, axis=params.bulbAxis):
  p = misc.Spherical.xyz(1, phi, theta)
  for i in range(3):
    p[i] *= axis[i]/2.0
    p[i] += params.bulbCenter[i]
  return p

def geodist(q, p):
  phiq, thetaq = p2e(q)
  phip, thetap = p2e(p)

  if phiq < phip:
    def swap(a, b):
      return b, a
  
    phip, phiq = swap(phip, phiq)
    thetap, thetaq = swap(thetap, thetaq)

  if phiq > phip and (phiq - phip) % (2 * pi) > pi:
    phiq = -(2 * pi - phiq)

  def pt(t):
    phi = (phiq-phip)*t+phip
    theta = (thetaq-thetap)*t+thetap
    return e2p(phi, theta)

  t = 0.0
  
  dt = (1.0/360*2*pi)/max([abs(phiq-phip), abs(thetaq-thetap)])
  tot = 0.0
  a = pt(0)
  seq = [a]
  while t < 1:
    t += dt
    b = pt(t)
    seq.append(b)
    tot += misc.distance(a, b)
    a = b
  return tot, seq

def glomdist(i, j):
  gl1 = params.glomRealCoords[i]
  gl2 = params.glomRealCoords[j]
  return geodist(gl1, gl2)[0]
  

