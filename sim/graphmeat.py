radius_factor = 2.0
from mayavi import mlab
from mayavi.mlab import figure
fig = figure(bgcolor=(0,0,0))

from tvtk.api import tvtk
from misc import Spherical as sph, convert as convdir
from numpy import pi, sin, cos

# render semaphore
class render:
  __count = 0

  @staticmethod
  def down():
    render.__count += 1
    fig.scene.disable_render = True
    
  @staticmethod
  def up():
    if render.__count > 0:
      render.__count -= 1
      
    if render.__count == 0:
      fig.scene.disable_render = False  

def get_line(a, b):
  src = tvtk.LineSource(point1=a, point2=b)
  mapper = tvtk.PolyDataMapper(input=src.output)
  actor = tvtk.Actor(mapper=mapper)
  fig.scene.add_actor(actor)
  return actor

def get_trunkcone(b, a):
  phi_base, theta_base = sph.to(a, b)[1:]

  quads = tvtk.CellArray() #vtk.vtkCellArray()
  points = tvtk.Points()   #vtk.vtkPoints()
  Nface = 3
  for i in range(Nface+1):
    # rotate
    phi, theta = convdir((i%Nface)*2*pi/Nface, pi*0.5, phi_base, theta_base)

    # generate  new points
    p = tuple(sph.xyz(a[3]*0.5*radius_factor, phi, theta, a[:3]))
    q = tuple(sph.xyz(b[3]*0.5*radius_factor, phi, theta, b[:3]))

    # insert points
    points.append(p)
    points.append(q)

    if i >= 1:
      # create a face            
      quad = tvtk.Quad()
      n = points.number_of_points-1

      quad.point_ids.set_id(0, n-3) # p
      quad.point_ids.set_id(1, n-2) # q
      quad.point_ids.set_id(2, n)   # q
      quad.point_ids.set_id(3, n-1) # p

      # insert the new face
      quads.insert_next_cell(quad)

  # create the actor
  polydata = tvtk.PolyData(points=points, polys=quads)
  mapper = tvtk.PolyDataMapper(input=polydata)
  actor = tvtk.Actor(mapper=mapper)
  fig.scene.add_actor(actor)
  return actor

def get_cone(base, radius, v):
  if type(base) != tuple:
    base = tuple(base)
  if type(v) != tuple:
    v = tuple(v)
  src = tvtk.ConeSource(center=base, radius=radius*radius_factor, height=radius, direction=v, resolution=20)
  mapper = tvtk.PolyDataMapper(input=src.output)
  actor = tvtk.Actor(mapper=mapper)
  fig.scene.add_actor(actor)
  return actor

def get_sphere(p, radius, res=8):
  if type(p) != tuple:
    p = tuple(p)
  src = tvtk.SphereSource(center=p, radius=radius, phi_resolution=res, theta_resolution=res)
  mapper = tvtk.PolyDataMapper(input=src.output)
  actor = tvtk.Actor(mapper=mapper)
  fig.scene.add_actor(actor)
  return actor

def get_many_spheres(pts, radius, res=32):
  actors = []
  render.down()
  for p in pts:
    actors.append(get_sphere(p, radius, resolution=res))
  render.up()
  return actors

def get_ellipsoid(center, axis, res=8):
  dphi = 2*pi/res
  dtheta = pi/res
  [phi, theta] = numpy.mgrid[0:2*pi+dphi:dphi, 0:pi+dtheta:dtheta]
  x = axis[0]*0.5*cos(phi)*sin(theta)+center[0]
  y = axis[1]*0.5*sin(phi)*sin(theta)+center[1]
  z = axis[2]*0.5*cos(theta)+center[2]
  return mlab.mesh(x, y, z, color=(0,0,0)).actor

def get_mesh(x, y, z):
  return mlab.mesh(x, y, z, color=(0,0,0)).actor

def remove_actor(actor):
  fig.scene.remove_actor(actor)
  

def start():
  mlab.show()
