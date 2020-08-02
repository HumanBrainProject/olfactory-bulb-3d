from common import h, pc
import modeldata
import gidfunc

'''
Interested in
Number of granules that go to mitral and mtufted (regardless of glomerulus)
Number of granules to each mitral
Number of granules to each mTufted
Number of granules to each glomerulus
Number of granules that go to more than one mitral in a glomerulus
Number of granules that go to more than one mtufted in a glomerulus

call them
ng2mmt
ng2eachm
ng2eachmt
ng2eachgl
ng2moremInGl
ng2moremtInGl

Can present as min, max, average.
'''

def chk_gran_conn():
  model = modeldata.getmodel()
  ggids = model.granule_gids
  mgids = model.mitral_gids
  mgrss = model.mgrss

  # for each granule, list of all mgid it connects to and vice versa
  g2m = {}
  m2g = {}
  for mgrs in mgrss.values():
    ggid = mgrs.ggid
    mgid = mgrs.mgid
    if mgrs.gd: # granule exists on this rank
      if ggid not in g2m:
        g2m[ggid] = []
      g2m[ggid].append(mgid)
    if mgrs.md: # mitral or mtufted exists on this rank
      if mgid not in m2g:
        m2g[mgid] = []
      m2g[mgid].append(ggid)

  a='Number of granules that go to mitral and mtufted (regardless of glomerulus)'
  na = 0
  for ms in g2m.values():
    nmit = 0
    nmtuft = 0
    for mgid in ms:
      nmit += 1 if gidfunc.ismitral(mgid) else 0
      nmtuft += 1 if gidfunc.ismtufted(mgid) else 0
    na += 1 if nmit > 0 and nmtuft > 0 else 0
  na = int(pc.allreduce(na, 1))
  if pc.id() == 0:
    print("%d %s" %(na, a))

  a='[total,imin,imax,iavg,xmin,xmax,xavg] granule connections to mitral'
  b='[total,imin,imax,iavg,xmin,xmax,xavg] granule connections to mtuft'
  nab=[[[],[],[],[]],[[],[],[],[]]]

  for ms in g2m.values():
    # assume if first is mitral then all are mitrals otherwise mtuft
    dat = nab[0] if gidfunc.ismitral(ms[0]) else nab[1]

    # want to distinguish intra mitral, distinct mitral, and any mitral
    # generate map of distinct:count for that distinct instance
    distinct = {}
    for d in set(ms):
      distinct[d] = 0
    for m in ms:
      distinct[m] += 1
    
    n_any = len(ms)
    n_distinct_m = len(distinct)
    n_intra_m_min = min(distinct.values())
    n_intra_m_max = max(distinct.values())
    dat[0].append(n_any)
    dat[1].append(n_distinct_m)
    dat[2].append(n_intra_m_min)
    dat[3].append(n_intra_m_max)

  def nhost_len(v):
    return int(pc.allreduce(len(v), 1))

  def nhost_sum(v):
    return int(pc.allreduce(sum(v), 1))

  def nhost_max(v):
    return int(pc.allreduce(max(v), 2))

  def nhost_min(v):
    return int(pc.allreduce(min(v), 3))

  def pr0(s):
    if pc.id() == 0:
      print(s)

  def pr(title, dat):
    i = 0
    pr0(title)
    totg = nhost_len(dat[i])
    pr0("%d granules of this type" % totg)
    pr0("%d total connections" % nhost_sum(dat[i]))
    if totg:
      pr0("%d min ; %d max ; %g avg" % (nhost_min(dat[i]), nhost_max(dat[i]), float(nhost_sum(dat[i]))/totg))

  pr(a, nab[0])
  pr(b, nab[1])

if __name__ == "__main__":
  chk_gran_conn()

