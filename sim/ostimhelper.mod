NEURON {
  THREADSAFE
  ARTIFICIAL_CELL OdorStimHelper
  RANGE start, dur, invl_min, invl_max
  BBCOREPOINTER space
}

PARAMETER {
  start = 0 (ms)
  dur = 0 (ms)
  invl_min = 1 (ms)
  invl_max = 2 (ms)
}

ASSIGNED {
  space
}

INITIAL {
  initstream()
  if (t <= start) {
    net_send(start, 1)
  }
}

FUNCTION invl()(ms) {
  invl = (invl_max - invl_min)*uniform_pick() + invl_min
}

NET_RECEIVE(dummy) {
  LOCAL tinv
  if (flag == 1) {
    net_event(t)
    tinv = invl()
    if (t + tinv <= dur) {
      net_send(tinv, 1)
    }
  }
}

:::::::::::::::::::::::::::::::::::::::::::::::::::::

VERBATIM
#include "nrnran123.h"
ENDVERBATIM

PROCEDURE initstream() {
VERBATIM
  if (_p_space) {
    nrnran123_setseq((nrnran123_State*)_p_space, 0, 0);
  }
ENDVERBATIM
}

FUNCTION uniform_pick() {
VERBATIM
  if (_p_space) {
    _luniform_pick = nrnran123_dblpick((nrnran123_State*)_p_space);
  }else{
    _luniform_pick = 0.5;
  }
ENDVERBATIM
}

PROCEDURE noiseFromRandom123() {
VERBATIM
#if !NRNBBCORE
 {
  nrnran123_State** pv = (nrnran123_State**)(&_p_space);
  if (*pv) {
    nrnran123_deletestream(*pv);
    *pv = (nrnran123_State*)0;
  }
  *pv = nrnran123_newstream3((uint32_t)*getarg(1), (uint32_t)*getarg(2), (uint32_t)*getarg(3));
 }
#endif
ENDVERBATIM
}

VERBATIM
static void bbcore_write(double* x, int* d, int* xx, int *offset, _threadargsproto_) {
#if !NRNBBCORE
  /* error if using the legacy normrand */
  if (!_p_space) {
    fprintf(stderr, "OStimHelper: noiseFromRandom123(1,2,3) not called.\n");
    assert(0);
  }
  if (d) {
    uint32_t* di = ((uint32_t*)d) + *offset;
    nrnran123_State** pv = (nrnran123_State**)(&_p_space);
    nrnran123_getids3(*pv, di, di+1, di+2);
  }
  *offset += 3;
#endif
}

static void bbcore_read(double* x, int* d, int* xx, int* offset, _threadargsproto_) {
  assert(!_p_space);
  uint32_t* di = ((uint32_t*)d) + *offset;
  nrnran123_State** pv = (nrnran123_State**)(&_p_space);
  *pv = nrnran123_newstream3(di[0], di[1], di[2]);
  *offset += 3;
}
ENDVERBATIM

