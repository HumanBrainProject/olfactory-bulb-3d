from neuron import h
from grow import *

# write a single section on hoc

def _writeSection(fw, points, secname):

    MAXPOINTS = 199

    fw.write(secname + " {\n\tpt3dclear()\n")



    for i in range(len(points)):

        if i > 0 and not (i % MAXPOINTS):

            fw.write("}\n\n" + secname + " {\n")



        fw.write("\tpt3dadd(")

        

        fw.write(str(points[i][0]))

        for j in range(1, 4):

            fw.write(", " + str(points[i][j]))

            

        fw.write(")\n")

    fw.write("}\n\n")



# write nrn in fw

def _saveNeuron(fw, nrn, somaName, apicName, dendName, tuftName):



    # write creates on file

    def writeCreate(fw, name, N):

        if N <= 0:

            return

        

        fw.write("create " + name)

        if N > 1:

            fw.write("[" + str(N) + "]")

        fw.write("\n")



    # write connection string

    def writeConn(fw, sonName, parentName, ison, iparent, x):

        fw.write("connect " + sonName)

        if ison >= 0:

            fw.write("[" + str(ison) + "]")

        fw.write("(0), " + parentName)

        if iparent >= 0:

            fw.write("[" + str(iparent) + "]")

        fw.write("(" + str(x) + ")\n")



    # create for the section!

    writeCreate(fw, somaName, 1)





    # write soma

    _writeSection(fw, nrn.soma.points, somaName)

    fw.write("\n\n\n")

    # write apical
    if nrn.apic:

        writeCreate(fw, apicName, 1)

        _writeSection(fw, nrn.apic.points, apicName)

        fw.write("\n\n\n")
        
        writeConn(fw, apicName, somaName, -1, -1, .5)

    

    # write tuft
    if len(nrn.tuft) > 0 :
        writeCreate(fw, tuftName, len(nrn.tuft))
        for x in nrn.tuft:
            _writeSection(fw, x.points, tuftName + "[" + str(x.index) + "]")

        fw.write("\n\n\n")
        for x in nrn.tuft: writeConn(fw, tuftName, apicName, x.index, -1, 1)




    # write dendrites
    if len(nrn.dend) > 0:
        writeCreate(fw, dendName, len(nrn.dend))
        for x in nrn.dend:
            _writeSection(fw, x.points, dendName + "[" + str(x.index) + "]")
        fw.write("\n\n\n")
        # make connections
        for x in nrn.dend:
            if x.parent == nrn.soma:
                writeConn(fw, dendName, somaName, x.index, -1, .5)
            else:
                writeConn(fw, dendName, dendName, x.index, x.parent.index, 1)
        fw.write("\n\n\n\n\n\n")



# save neurons

def saveNeurons(nrns, fname):

    fw = open(fname, "w")
    fw.write("load_file(\"nrngui.hoc\")\r\n")
    if type(nrns) == list:

        for i in range(len(nrns)):

            n = str(i)

            _saveNeuron(fw, nrns[i], "soma" + n, "apic" + n, "dend" + n, "tuft" + n)

    else:

        _saveNeuron(fw, nrns, "soma", "apic", "dend", "tuft")

    fw.close()



# show the network

def genNetwork(gloms, fname):

    fw = open(fname, "w")

    fw.write("load_file(\"nrngui.hoc\")\n")

    for g in gloms:

        for i in range(Nmitral_per_glom):

            mid = g * Nmitral_per_glom + i

            nrn = genMitral(mid)

            print("mitral ", mid)

            

            stmid = str(mid)

            _saveNeuron(fw, nrn, "soma" + stmid, "apic" + stmid, "dend" + stmid, "tuft" + stmid)    

    fw.close()



# return gloms

def getGloms(gloms):

    newgloms = []

    for g in gloms:

        for i in range(Nmitral_per_glom):

            mid = g * Nmitral_per_glom + i

            newgloms += [ genMitral(mid) ]

            print("mitral ", mid)



    return newgloms



# show glomerulus



# generate mitrals

def genMitrals(mids, fname):

    fw = open(fname, "w")

    fw.write("load_file(\"nrngui.hoc\")\n")

    for g in mids:

        nrn = genMitral(g)

        print("mitral ", g)

            

        stmid = str(g)

        _saveNeuron(fw, nrn, "soma" + stmid, "apic" + stmid, "dend" + stmid, "tuft" + stmid)    

    fw.close()

# sampling
def sampleMitral(fname):
    r = ranstream(0, 2)
    mids = []
    for i in range(len(glomsCoords)):
        mids.append(i * Nmitral_per_glom + int(r.discunif(0, 4)))
    genMitrals(mids, fname)

#n=[]


#for i in [ 100, 150, 300]:
#n.append(genMitral(100))
#saveNeurons(n, "test.hoc")
#h.load_file("test.hoc")
#h.load_file("select.hoc")
#h.load_file("nrngui.hoc")
#from mkmitral import *

#for i in range(127):
#    print i
#   n.append(mkmitral(i*5))

#h.load_file("select.hoc")
#m = mkmitral(82)
#h.load_file("select.hoc")

    
