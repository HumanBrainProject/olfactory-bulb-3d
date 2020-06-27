from common import *

''' destroy mitrals, granules, MGRS, and clear internal gid maps. '''
def destroy_model(model):
  pc.gid_clear()
  model.mgrss = {}
  model.granules = {}
  model.mitrals = {}
  model.mgid2piece = {}
  model.gj = {}
  model.mt2blanes.clear()
  model.blanes_gids.clear()
  model.blanes.clear()
  model.blanes2gc.clear()
  model.blanes2gc_connections.clear()
  model.mt2blanes_connections.clear()

