import pathdist
import bindict
import gidfunc
import params
import fileinput
wexc_mc = []
wexc_mt = []
winh_mc = []
winh_mt = []
for l in fileinput.input('../weightse1.25i0.4i0.4kdrmt0.3ks0.005.txt'):
  tk = l.split()
  wexc_mc += [float(tk[1])]
  winh_mc += [float(tk[2])]
  wexc_mt += [float(tk[3])]
  winh_mt += [float(tk[4])]



for perc in [0,50,100]:


  bindict.load('fullbulb%d-v4.dic'%perc)


  for w_base in [0]:

    for glomid in [2,10,17,33,126,99,113,5,77,105,47,98,16,8,27]:
      
      filename = 'w%dcontrol%dp%de1.25i0.04i0.04' % (w_base, glomid, perc)

      gloms = set([ 37, glomid ])

      def issynapse(gid): return not (gidfunc.ismitral(gid) or gidfunc.ismtufted(gid) or gidfunc.isgranule(gid))

      def glom2mgid(glomid):
        for i in range(glomid * params.Nmitral_per_glom, (glomid + 1) * params.Nmitral_per_glom):
          yield i + params.gid_mitral_begin
        for i in range(glomid * params.Nmtufted_per_glom, (glomid + 1) * params.Nmtufted_per_glom):
          yield i + params.gid_mtufted_begin


      with open(filename+'.weight.dat', 'w') as fo:
        for _glomid in gloms:
          for mgid in glom2mgid(_glomid):
            for gid in bindict.mgid_dict[mgid]:
              if issynapse(gid):
                ii = int(pathdist.pd(gid)/20)
                if gidfunc.ismitral(mgid):
                  wexc = wexc_mc[ii]
                  winh = winh_mc[ii]
                else:
                  wexc = wexc_mt[ii]
                  winh = winh_mt[ii]


                
                fo.write('%d %d 0\n' % (gid, wexc))
                fo.write('%d %d 0\n' % (gid-1, winh))
      print w_base, glomid, perc

    
    
