from growdef import *
from struct  import unpack

class CellReader:
  
  def __init__(self, filename):
    self.__fi = open(filename, 'rb')
    
    self.__cell_offset = [None]*unpack('>I', self.__fi.read(4))[0]
    for i in range(len(self.__cell_offset)):
      self.__cell_offset[i] = unpack('>I', self.__fi.read(4))[0]
    
    dataoffset = self.__fi.tell()
    for i in range(len(self.__cell_offset)):
      self.__cell_offset[i] += dataoffset
      

      
      
  def close(self):
    self.__fi.close()

    

  def __readsections(self, sections):
    nsec = unpack('>H', self.__fi.read(2))[0]
    for isec in range(nsec):
      sec = Section()
      npt = unpack('>I', self.__fi.read(4))[0]
      for ipt in range(npt):
        sec.points.append(unpack('>ffff', self.__fi.read(16)))
      sections.append(sec)

    

  def __connect(self, cell):

    def get_section(sectype, isec):
      if sectype == 0:
        return cell.soma[isec]
      elif sectype == 1:
        return cell.apic[isec]
      elif sectype == 2:
        return cell.tuft[isec]
      elif sectype == 3:
        return cell.dend[isec]
      return None
        
    
    nconn = unpack('>I', self.__fi.read(4))[0]
    for i in range(nconn):
      sectype1 = unpack('>B', self.__fi.read(1))[0]
      isec1 = unpack('>H', self.__fi.read(2))[0]

      sectype2 = unpack('>B', self.__fi.read(1))[0]
      isec2 = unpack('>H', self.__fi.read(2))[0]

      sec1 = get_section(sectype1, isec1)
      sec2 = get_section(sectype2, isec2)

      sec1.parent = sec2
      sec2.children.append(sec1)
                       
    
                             
  def readcell(self, gid):
    cell = Neuron()
    self.__fi.seek(self.__cell_offset[gid])
    self.__readsections(cell.soma)
    self.__readsections(cell.apic)
    self.__readsections(cell.tuft)
    self.__readsections(cell.dend)
    self.__connect(cell)
    return cell
    

if __name__ == '__main__':
  cr = CellReader('../bulbvis/cells.car')
  cell = cr.readcell(185)
