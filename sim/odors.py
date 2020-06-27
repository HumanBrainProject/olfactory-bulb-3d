import misc


odors = {}

def hill(eta, k, n, Fmax, cc): return Fmax/(1+((1+(0.0+k)/cc)/eta)**n)
def PG(val): return 0.5/(1+0.01*(1.0/val-1))

class odor:
  def __init__(self, name, eta, k):
    self.name = name
    self.eta = eta
    self.k = k
    
  def getORNs(self, cc):
    return [ hill(self.eta[i], self.k[i], 2, 25.0, cc) for i in range(len(self.eta)) ]

  def afterPG_1(self, cc):
    act = self.getORNs(cc)
    mu = misc.mean(act)
    for i in range(len(act)):
      act[i] -= mu
      if act[i] < 0:
        act[i] = 0
    return act
      
  def afterPG_2(self, cc):
    act = self.afterPG_1(cc)
    for i in range(len(act)):
      if act[i] > 0:
        act[i] -= PG(act[i])
        if act[i] < 0:
          act[i] = 0
    return act

    

def init(kfilename, etafilename):
  odors.clear()
  
  import fileinput
  
  for l in fileinput.input(etafilename):
    data = l.split('\t')
    odors.update({ data[0]: odor(data[0], [ float(x) for x in data[1:] ], []) })
    
  for l in fileinput.input(kfilename):
    data = l.split('\t')
    odors[data[0]].k = [ float(x) for x in data[1:] ]
    

init('Kod.txt', 'Eta.txt')

if __name__ == '__main__':
  o = odors['Mint']
