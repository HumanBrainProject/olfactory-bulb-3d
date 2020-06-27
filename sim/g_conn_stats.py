import custom_params as cp; cp.filename = 'glomcfg27'
import bindict; bindict.load('miscd27c10.dic')
import granules
fo = open('gconnstats.txt', 'w')
g = {}
for ggid, conn in bindict.ggid_dict.items():
    fo.write('%g\n'%len(conn))
fo.close()
