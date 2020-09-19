import custom_params as cp
cp.filename='glomcfg27'
from params import *
from misc import *
from random import random

glomEll = Ellipsoid(bulbCenter, glomAxis)

N_TOTAL_GLOMS = 1800.
REAL_GLOMS_XY_FNAME = 'glomxy.txt'
REALGLOMS_FNAME = 'realgloms.txt'
FALSEGLOMS_FNAME = 'falsegloms.txt'
glomRealCoords = []
glomFalseCoords = []
cuttingY = 2200

def loadGloms():
    def _loadGloms(fname, vect):
        # load gloms positions
        f = open(fname)
        line = f.readline()
        while line:
            token = line.split()
            # every line has N glom X Y of i-glomerolous
            x = float(token[0]); y = float(token[1]); z = float(token[2])
            vect.append([ x, y, z ])
            line = f.readline()
        ###
    _loadGloms(REALGLOMS_FNAME, glomRealCoords)
        
def bulbHalfAxisZ(theta):
    if theta > pi: theta %= pi
    if theta >= 0. and theta <= pi / 2:
        return glomAxis[2] / 2
    y0 = glomAxis[2] / 2
    x0 = pi / 2
    b = 0.52
    a = 300. / (abs(pi / 2) ** b)
    return y0 + a * abs(theta - x0) ** b



def readRealGloms():
    # load gloms positions
    f = open(REAL_GLOMS_XY_FNAME)
    line = f.readline()
    while line:
        token = line.split()
        # every line has N glom X Y of i-glomerolous
        x = float(token[0]); y = float(token[1])
        # force z to put glomerulus on Ellipsoid surface
        z = glomEll.getZ([ x, y ])
        glomRealCoords.append([ x, y, z ])
        line = f.readline()

def resolveCollision():
    glomE = Ellipsoid(bulbCenter, glomAxis)
    
    def move(v, sign, d, j, coordi):
        d *= .5
        for i in range(len(v)):
            
            if i == j: continue
            if sign < 0:
                if v[j][coordi] >= v[i][coordi]:
                    v[i][coordi] += sign * d
                    v[i][2] = glomE.getZ(v[i][0:2])
                else:
                    v[i][coordi] -= sign * d
                    v[i][2] = glomE.getZ(v[i][0:2])
            else:
                if v[j][coordi] < v[i][coordi]:
                    v[i][coordi] += sign * d
                    v[i][2] = glomE.getZ(v[i][0:2])
                else:
                    v[i][coordi] -= sign * d
                    v[i][2] = glomE.getZ(v[i][0:2])
        v[j][coordi] += sign * d
        v[j][2] = glomE.getZ(v[j][0:2])
            
        


    for i in range(len(glomRealCoords) - 1):
        for j in range(i + 1, len(glomRealCoords)):
            if distance(glomRealCoords[i], glomRealCoords[j]) < 2 * GLOM_RADIUS:
                d = 2 * GLOM_RADIUS - distance(glomRealCoords[i], glomRealCoords[j])
                if glomRealCoords[i][0] < glomRealCoords[j][0]:
                    move(glomRealCoords, -1, d * .5, i, 0)
                elif glomRealCoords[i][0] > glomRealCoords[j][0]:
                    move(glomRealCoords, 1, d * .5, i, 0)
                if glomRealCoords[i][1] < glomRealCoords[j][1]:
                    move(glomRealCoords, -1, d * .5, i, 1)
                elif glomRealCoords[i][1] > glomRealCoords[j][1]:
                    move(glomRealCoords, 1, d * .5, i, 1)

                    
def genFalseGloms():
    global glomRealCoords
    global glomFalseCoords
    error = 0.
    depInRealZone = 30.
    
    halfAxis = copy(glomAxis)
    if len(glomRealCoords) <= 0: readRealGloms()
    allGloms = copy(glomRealCoords)
    for i in range(len(halfAxis)): halfAxis[i] /= 2
    
    def genGlom():
        phi = random() * 2 * pi
        theta = random() * pi
        depth = random() * 50.
        
        x = sin(theta) * cos(phi) * (halfAxis[0] + depth) + bulbCenter[0]
        y = sin(theta) * sin(phi) * (halfAxis[1] + depth) + bulbCenter[1]
        z = cos(theta) * (bulbHalfAxisZ(theta) + depth) + bulbCenter[2]
        return [ x, y, z ], depth
    
    def noGood(newGl, dep, flag):
        if newGl[1] > cuttingY:
            return True
        
        # prevent excess of sovrapposition with real gloms
        #if flag:
        #    if not (newGl[0] >= -107. and newGl[1] >= -119. and newGl[0] <= 1096. and newGl[1] <= 2126.):
        #        return True
        #    elif (newGl[2] < 0.):
        #        return True
        #    elif abs(dep) > 30.:
        #        return True
            
        #if not flag and ((newGl[0] >= -107. and newGl[1] >= -119. and newGl[0] <= 1096. and newGl[1] <= 2126.) and newGl[2] > 0.):
        #    return True
        #if newGl[0] >= -100 and newGl[1] >= -100 and newGl[0] <= 1100. and newGl[1] <= 2100 and abs(dep) > 10.:
         #   return True
        
        for j in range(len(allGloms)):
            if distance(allGloms[j], newGl) < 2 * GLOM_RADIUS:
                return True
            
        return False


    for i in range(270):
        newGl, dep = genGlom()
        while noGood(newGl, dep, True):
            newGl, dep = genGlom()
        allGloms.append(newGl)
        
    while len(allGloms) < N_TOTAL_GLOMS:
        print("Gloms are ", len(allGloms))
        newGl, dep = genGlom()
        while noGood(newGl, dep, False):
            newGl, dep = genGlom()
        allGloms.append(newGl)

    #print "Resolve collisions between gloms"
    #resolveCollision(allGloms)
    #glomRealCoords = allGloms[:len(glomRealCoords)]
    glomFalseCoords = allGloms[len(glomRealCoords):]

def saveGloms():
    def _save(fname, gloms):
        f = open(fname, 'w')
        for p in gloms:
            f.write(str(p[0]) + " " + str(p[1]) + " " + str(p[2]) + "\r\n")
        f.close()
    ##
    _save(REALGLOMS_FNAME, glomRealCoords)
    _save(FALSEGLOMS_FNAME, glomFalseCoords)


if __name__ == '__main__':
    #readRealGloms()
    #loadGloms()
    #resolveCollision()

    genFalseGloms()
    saveGloms()
    quit()
    
    

                    
                    
            
        
    
