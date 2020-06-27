import params

def mgid2glom(gid):
  if ismitral(gid):
    return int((gid - params.gid_mitral_begin) / params.Nmitral_per_glom)
  elif ismtufted(gid):
    return int((gid - params.gid_mtufted_begin) / params.Nmtufted_per_glom)
  return None

def blanes2glom(gid):
  return (gid-params.gid_blanes_begin)/params.NBlanes_per_glom 

def ismitral(gid):
  return gid >= params.gid_mitral_begin and gid < params.gid_mitral_begin+params.Nmitral

def ismtufted(gid):
  return gid >= params.gid_mtufted_begin and gid < params.gid_mtufted_begin+params.Nmtufted

def isgranule(gid):
  return gid >= params.gid_granule_begin and gid < params.gid_granule_begin+params.Ngranule

def isblanes(gid):
  return gid >= params.gid_blanes_begin and gid < params.gid_blanes_begin+params.NBlanes
  
  
def mgrs_gid(gid_source, gid_target, slot=0):
  if (gid_source < params.gid_granule_begin): #detector on mitral
    i = (gid_target*params.Ngloms + mgid2glom(gid_source) + 1)*2 + params.gid_mgrs_begin 
  else: #detector on granule
    i = (gid_source*params.Ngloms + mgid2glom(gid_target) + 1)*2 + params.gid_mgrs_begin - 1
  return i


def mbs_gid(gid_source, gid_target):
  return (gid_target-params.gid_blanes_begin)*params.Nmtufted+(gid_source-params.gid_mtufted_begin)+params.gid_mbs_begin
  
def bc2gc_gid(gid_source, gid_target):  
  return (gid_source-params.gid_blanes_begin)*params.Ngranule+(gid_target-params.gid_granule_begin)+params.gid_bc2gc_begin

