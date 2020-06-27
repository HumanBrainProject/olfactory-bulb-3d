
from struct import pack
from os import system

class CellWriter:
  def __init__(self, filename):
    ''' sequential writer for cells '''
    self.name = filename+'.car'
    self.__fname = ['%s.ncell'%filename,'%s.header'%filename,'%s.data'%filename]
    self.__fo_ncell = open(self.__fname[0], 'wb')
    self.__fo_header = open(self.__fname[1], 'wb')
    self.__fo_data = open(self.__fname[2], 'wb')
    self.__ncell = 0


  def close(self):
    self.__fo_ncell.write(pack('>I', self.__ncell))
    self.__fo_header.close()
    self.__fo_data.close() 
    self.__fo_ncell.close()

    # merging
    with open(self.name, 'wb') as fo:
      for fname in self.__fname:
        with open(fname, 'rb') as fi:
          b = fi.read(1)
          while b:
            fo.write(b)
            b = fi.read(1)
          
    system('rm %s %s %s' % \
           (self.__fo_header.name,\
            self.__fo_data.name,\
            self.__fo_ncell.name,\
            )
           )


    
  def write(self, cell):
    ''' write a cell '''
    
    def writesections(sections):
      self.__fo_data.write(pack('>H', len(sections))) #n sections
      for s in sections:
        self.__fo_data.write(pack('>I', len(s.points))) #n points
        for p in s.points:
          self.__fo_data.write(pack('>ffff', *p)) #point


    def writeconnectivity(cell):
      # number of connections
      nconn = 0
      for s in cell.soma+cell.apic+cell.tuft+cell.dend:
        if s.parent:
          nconn += 1
      self.__fo_data.write(pack('>I', nconn))
      
      def write_conn(secid1, sections):
        for isec1, s in enumerate(sections):
          if s.parent:
            try:
              isec2 = cell.soma.index(s.parent); secid2 = 0
            except ValueError: pass
            try:
              isec2 = cell.apic.index(s.parent); secid2 = 1
            except ValueError: pass
            try:
              isec2 = cell.tuft.index(s.parent); secid2 = 2
            except ValueError: pass   
            try:
              isec2 = cell.dend.index(s.parent); secid2 = 3
            except ValueError: pass          
            self.__fo_data.write(pack('>BHBH', secid1, isec1, secid2, isec2))
          
      write_conn(0, cell.soma)
      write_conn(1, cell.apic)
      write_conn(2, cell.tuft)
      write_conn(3, cell.dend)


    # write everything
    self.__fo_header.write(pack('>I', self.__fo_data.tell()))
    writesections(cell.soma)
    writesections(cell.apic)
    writesections(cell.tuft)
    writesections(cell.dend)
    writeconnectivity(cell)
    self.__ncell += 1



if __name__ == '__main__':
  from grow import genMitral,genMTufted
  from params import Nmitral as nmc, Nmtufted as nmtc
  ncell = nmc
  cw = CellWriter('../vis/mccells')
  for gid in range(635):
    cw.write(genMitral(gid))
    print 'cell', gid, 'generated and stored'
  for gid in range(635,635+10*127):
    cw.write(genMTufted(gid))
    print 'cell', gid, 'generated and stored'
  cw.close()
