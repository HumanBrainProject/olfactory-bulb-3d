# spike read spikes and print using
# matplotlib the data

# hebbian step func.
aLTP=2e-2
aLTD=2e-2
tauLTP=20.
tauLTD=20.
delay_post=3
delay_pre=1
wmax=1.

ltdinvl_excit = 250.
ltpinvl_excit = 33.33
sighalf_excit = 25.0
ltdinvl_inhib = 250.
ltpinvl_inhib = 33.33
sighalf_inhib = 25.0
import params
def syn_hebb(ispre, w, tpre, tpost, P, M, t):
  from math import exp
  if ispre:
    P=P*exp((tpre-t)/tauLTP)+aLTP
    interval=tpost-t
    dw=wmax*M*exp(interval/tauLTD)
  else:
    M=M*exp((tpost-t)/tauLTD)-aLTD
    interval=t-tpre
    dw=wmax*P*exp(-interval/tauLTP)

  w += dw
  if w > wmax: w = wmax
  elif w < 0: w = 0
  return w, P, M

def hebbian(winit, trpre, trpost):
  # this destroy vector data
  for i in range(len(trpre)):
    trpre[i] += delay_pre
  for i in range(len(trpost)):
    trpost[i] += delay_post

  t=[0]
  w=[winit]
  P=M=0
  i=j=1
  while i<len(trpre) and j<len(trpost):
    if trpre[i] <= trpost[j]:
      ispre=True
      t.append(trpre[i])
    else:
      ispre=False
      t.append(trpost[j])
    wnew,P,M=syn_hebb(ispre,w[-1],trpre[i-1],trpost[j-1],P,M,t[-1])
    w.append(wnew)
    if ispre:
      i+=1
    else:
      j+=1

  for i in range(i,len(trpre)):
    t.append(trpre[i])
    wnew,P,M=syn_hebb(True,w[-1],trpre[i-1],trpost[j-1],P,M,t[-1])
    w.append(wnew)   

  for j in range(j,len(trpost)):
    t.append(trpost[j])   
    wnew,P,M=syn_hebb(False,w[-1],trpre[i-1],trpost[j-1],P,M,t[-1])
    w.append(wnew)

  return t, w

# non hebbian step



def syn_step(s, isi, excit=True):

  if excit:
    ltpinvl = ltpinvl_excit
    ltdinvl = ltdinvl_excit
    sighalf = sighalf_excit
  else:
    ltpinvl = ltpinvl_inhib
    ltdinvl = ltdinvl_inhib
    sighalf = sighalf_inhib

  if isi < ltpinvl:
    s += 1
  elif isi < ltdinvl:
    s -= 1
  if s > 2 * sighalf:
    s = 2 * sighalf
  elif s < 0:
    s = 0
  return s

def syn_weights(t, winit=0, excit=True):
  w = [ winit ]
  for i in range(1, len(t)):
    w.append(syn_step(w[-1], t[i] - t[i-1], excit))
  return w
    
    

class SpikesReader:
    
    def __init__(self, filename, *args):
        self.sort = False
        from struct import unpack
        self.cache_max_len = 100

        self.tstop = None
        
        self.bincoded = filename.endswith('.spk') or filename.endswith('.spk2')
        self.__initweights = {} # initial weights
        
        if len(args) > 0:
          f = open(args[0], 'r')
          line = f.readline()
          while line:
            gid, s = line.split()[:2]
            gid = int(gid)
            s = int(s)
            self.__initweights.update({ gid:s })
            line = f.readline()
          f.close()
          
        if self.bincoded:
          # init for binary format
          self.header = {}
          self.fi = open(filename, 'rb')
          
          offset = unpack('>q', self.fi.read(8))[0]

          # read the time
          if filename.endswith('.spk2'):
            self.tstop = unpack('>f', self.fi.read(4))[0]
            hlen = offset / 8
            offset += 4
          else:
            hlen = offset / 8

          offset += 8

          for j in range(hlen):
            gid, n = unpack('>LL', self.fi.read(8)) # read

            if gid not in self.header:
              self.header.update({ gid:[(offset, n)] })
            else:
              self.header[gid].append((offset, n)) 

            offset += n * 4
            
        else:
          # init for textual format
          self.fi = open(filename, 'r')

        self.__cache = {}
        self.__old = []

    def retrieve(self, gid):
        # if gid in cache don't retrieve
        if gid not in self.__cache:

            # clean the oldest
            if len(self.__cache) >= self.cache_max_len:
                del self.__cache[self.__old[0]]
                del self.__old[0]

            # read
            t = [ ]

            if self.bincoded:
              # binary format reading code
              offset, n = self.header[gid][-1]
#              for offset, n in self.header[gid]:
              self.fi.seek(offset)
              
              from struct import unpack
#              for i in range(n):
#                t.append(unpack('>f', self.fi.read(4))[0])
              t = list(unpack('>' + 'f'*n, self.fi.read(4*n)))
            else:
              # if not bincoded
              # it's the old textual format
              
              self.fi.seek(1)
              line = self.fi.readline()
              while line:
                tks = line.split()
                if int(tks[1]) == gid:
                  t.append(float(tks[0]))
                line = self.fi.readline()
              if len(t) == 0:
                raise KeyError
            # only for errors...
            if self.sort:
              t = sorted(t)
            self.__old.append(gid)    
            self.__cache.update({ gid:t })

        from copy import copy
        return copy(self.__cache[gid])
      
    def freqvssniff(self, gid, tstart=50.0):
      
        t = [ tstart+params.sniff_invl*0.5 ]
        nspk = [ 0 ]

        for x in self.retrieve(gid):
          i = int((x-tstart)/params.sniff_invl)
          if i >= len(t):
            t.append(t[-1]+params.sniff_invl*0.5)
            nspk.append(0)
          nspk[-1] += 1*1000.0/params.sniff_invl

        return t, nspk

    def frequency(self, gid):
        
        t = [ 0. ] + self.retrieve(gid)
        
        fr = [ 0. ]
        for i in range(1, len(t)):
            fr.append(1000. / (t[i] - t[i - 1]))

        return t, fr
      
    def stepvssniff(self, gid, tstart=50.0):
      return self.step(gid, dt=params.sniff_invl)
    
    def step(self, gid, dt=None, tlast=50.0):
        from mgrs import gid_mgrs_begin
        if gid < gid_mgrs_begin:
            return None
        if gid%2!=0 and params.use_fi_stdp:
          if gid in self.__initweights:
            wi=self.__initweights[gid] 
          else:
            wi=0
          tpre=[0.]
          if gid in self.header: tpre += self.retrieve(gid)
          tpost=[0.]
          if gid in self.header: tpost += self.retrieve(gid+1)
          t,w = hebbian(wi,tpre,tpost)
          return t,w         
        else:        
          t = [ 0. ]
          
          try:
            s = [ self.__initweights[gid] ]
          except KeyError:
            try:
              if gid%2:
                init_weight = params.init_inh_weight
              else:
                init_weight = params.init_exc_weight
            except:
              init_weight = 0
            s = [ init_weight ]

          try:
             t += self.retrieve(gid)
          except KeyError:
            return t, s
          
          if dt == None:
            for i in range(1, len(t)):
              s.append(syn_step(s[-1], t[i] - t[i-1], excit=(gid%2 == 0)))
            return t, s

          _t = [ ]
          _s = [ ]
          
          for i in range(1, len(t)):
            s.append(syn_step(s[-1], t[i] - t[i-1], excit=(gid%2 == 0)))

            if t[i]+params.sniff_invl > tlast:
              _t.append(tlast)
              _s.append(s[-1])
              tlast += params.sniff_invl
          return _t, _s

    def close(self):
        self.fi.close()





class SpikesWriter:
  def __init__(self, filename, tstop):
    self.filename = filename
    
    self.__fo = open(filename + '.data', 'wb')
    
    self.header = {}
    self.tstop = tstop

  def write(gid, t):
    from struct import pack
    self.header[gid] = len(t)
    self.__fo.write(pack('>'+('f'*len(t)), t))
    
  def close(self, filename):
    self.__fo.close()

    from struct import pack  
    
    fo = open(self.filename + '.time', 'wb')
    fo.write(pack('>f', self.tstop))
    fo.close()
    
    # write header
    fo = open(self.filename + '.header', 'wb')
    for x in list(self.header.items()):
      fo.write(pack('>LL', x))
    fo.close()
    
    from os import path
    fo = open(self.filename + '.size', 'wb')
    fo.write(pack('>q', path.getsize(self.filename + '.header')))
    fo.close()


    

# read time stop
tstop = 20050
try:
  from sys import argv
  tstop = float(argv[argv.index('-tstop') + 1])
except:
  pass
# @@@@@@@@@@@@@@

def show(sr, gids, xlabel, ylabel, call, title, ylim, legend=True):
    if len(gids) == 0:
      return
    from bindict import query as descr
    
    import matplotlib.pyplot as plt
    plt.figure()
    
    color = [ 'b', 'g', 'r', 'c', 'm', 'y', 'k' ]
    never_drawed = False
    for i, g in enumerate(gids):
        never_drawed = never_drawed | call(g, i, color[i % len(color)], descr(g)[-1])

    if not never_drawed:
      plt.close()
      return False

    if legend:
      plt.legend().draggable()
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    if len(ylim) == 2:
      plt.ylim(ylim)
    if sr.tstop:
      plt.xlim([ 0, sr.tstop ])
    elif tstop:
      plt.xlim([ 0, tstop ])
    plt.draw()
    return True

def show_raster(sr, gids):
    import matplotlib.pyplot as plt
    def raster(gid, i, col, descr):
        try:
          t = sr.retrieve(gid)
          plt.scatter(t, [ i ] * len(t), s=10, marker='|', label=descr, c=col)
        except KeyError:
          return False
        return True
    return show(sr, gids, 'spike time (ms)', '', raster, 'Spike raster', [ -1, len(gids) + 1 ])
        

def show_freqs(sr, gids):
    import matplotlib.pyplot as plt
    def freq(gid, i, col, descr):
        try:
          t, fr = sr.frequency(gid)
          plt.plot(t, fr, '-' + col + 'o', label=descr)
        except KeyError:
          return False
        return True

    return show(sr, gids, 'spike time (ms)', 'Freq. (Hz)', freq, 'Frequency', [])
            
        

def show_weights(sr, gids):
    from mgrs import gid_mgrs_begin
    
    # not weights
    gids = gids.difference(set(range(gid_mgrs_begin)))

    import matplotlib.pyplot as plt
    
    def step(gid, i, col, descr):
        try:
          t, d = sr.step(gid)
          if gid%2==0:
            maxsig=2*sighalf_excit
          elif params.use_fi_stdp:
            maxsig=wmax
          else:
            maxsig=2*sighalf_inhib

          for i in range(len(d)): d[i] = d[i]/maxsig #* maxsig

          plt.plot(t, d, col + '-', label=descr)
        except KeyError:
          return False
        return True
    return show(sr, gids, 'spike time (ms)', 'Step', step, 'Syn. Steps', [-0.1, 1.1])#[ -1, 2 * max(sighalf_inhib, sighalf_excit) + 1])    
        
def show_evol(sr, gids, tstart=50.0):
    import matplotlib.pyplot as plt
    def evol(gid, i, col, descr):
        try:
          if gid%2:
            ltpinvl=ltpinvl_inhib
            ltdinvl=ltdinvl_inhib
          else:
            ltpinvl=ltpinvl_excit
            ltdinvl=ltdinvl_excit
            
          t, fr = sr.frequency(gid)
          dw = [0]*len(fr)
          isniff = 0
          lastdw = 0
          for i in range(1, len(t)):
            _isniff = int(t[i]/params.sniff_invl)
            if _isniff > isniff:
              isniff = _isniff
              lastdw = 0
            if fr[i] >= 1000/ltpinvl:
              dw[i] = lastdw + 1
            elif fr[i] >= 1000/ltdinvl:
              dw[i] = lastdw - 1
            else:
              dw[i] = lastdw
            lastdw = dw[i]
          plt.plot(t, dw, '-' + col + 'o', label=descr)
        except KeyError:
          return False
        return True

    return show(sr, gids, 'spike time (ms)', 'DStep', evol, 'Evolution', [])


# main history
if __name__ == '__main__':
    
    from sys import argv
    i = argv.index('-i')
    

    
    gids = set()
    for sg in argv[argv.index('-gid') + 1:]:
        try:
          gids.add(int(sg))
        except ValueError:
          break

    sr = SpikesReader(argv[i + 1])
      
    # show all
    import matplotlib.pyplot as plt   
    show_freqs(sr, gids)
    show_weights(sr, gids)
    show_raster(sr, gids)
    plt.show()

    
