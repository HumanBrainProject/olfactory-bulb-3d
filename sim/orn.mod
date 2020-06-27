TITLE Fluctuating    conductances

COMMENT
-----------------------------------------------------------------------------

	Fluctuating conductance model for synaptic bombardment
	======================================================

THEORY

  Synaptic bombardment is represented by a stochastic model containing
  two fluctuating conductances g_e(t) and g_i(t) descibed by:

     Isyn = g_e(t) * [V - E_e] + g_i(t) * [V - E_i]
     d g_e / dt = -(g_e - g_e0) / tau_e + sqrt(D_e) * Ft
     d g_i / dt = -(g_i - g_i0) / tau_i + sqrt(D_i) * Ft

  where E_e, E_i are the reversal potentials, g_e0, g_i0 are the average
  conductances, tau_e, tau_i are time constants, D_e, D_i are noise diffusion
  coefficients and Ft is a gaussian white noise of unit standard deviation.

  g_e and g_i are described by an Ornstein-Uhlenbeck (OU) stochastic process
  where tau_e and tau_i represent the "correlation" (if tau_e and tau_i are 
  zero, g_e and g_i are white noise).  The estimation of OU parameters can
  be made from the power spectrum:

     S(w) =  2 * D * tau^2 / (1 + w^2 * tau^2)

  and the diffusion coeffient D is estimated from the variance:

     D = 2 * sigma^2 / tau


NUMERICAL RESOLUTION

  The numerical scheme for integration of OU processes takes advantage 
  of the fact that these processes are gaussian, which led to an exact
  update rule independent of the time step dt (see Gillespie DT, Am J Phys 
  64: 225, 1996):

     x(t+dt) = x(t) * exp(-dt/tau) + A * N(0,1)

  where A = sqrt( D*tau/2 * (1-exp(-2*dt/tau)) ) and N(0,1) is a normal
  random number (avg=0, sigma=1)


IMPLEMENTATION

  This mechanism is implemented as a nonspecific current defined as a
  point process.


PARAMETERS

  The mechanism takes the following parameters:

     E_e = 0  (mV)		: reversal potential of excitatory conductance

     g_e0 = 0.0121 (umho)	: average excitatory conductance

     std_e = 0.0030 (umho)	: standard dev of excitatory conductance

     tau_e = 2.728 (ms)		: time constant of excitatory conductance


Gfluct3: conductance cannot be negative


REFERENCE

  Destexhe, A., Rudolph, M., Fellous, J-M. and Sejnowski, T.J.  
  Fluctuating synaptic conductances recreate in-vivo--like activity in
  neocortical neurons. Neuroscience 107: 13-24 (2001).

  (electronic copy available at http://cns.iaf.cnrs-gif.fr)


  A. Destexhe, 1999

-----------------------------------------------------------------------------
ENDCOMMENT



INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
	POINT_PROCESS orn
	RANGE g_e, g_e_max, cc_peak, g_e_baseline
	RANGE std_e, tau_e, D_e
	NONSPECIFIC_CURRENT i
        THREADSAFE : only true if every instance has its own distinct Random
        POINTER donotuse
}

UNITS {
	(nA) = (nanoamp) 
	(mV) = (millivolt)
	(umho) = (micromho)
}

PARAMETER {
	dt		  (ms)
        
	E_e	= 0 	  (mV)            : reversal potential of excitatory conductance
	g_e_max	= 75e-3 (umho)          : average excitatory conductance
        cc_peak = 0     : (affinity*odor cc)
        
        g_e_baseline    = 0       (umho)          : background noise
	std_e	= 1e-3    (umho)	  : standard dev of excitatory conductance
	tau_e	= 400     (ms)            : time constant of excitatory conductance
}

ASSIGNED {
	v	(mV)		: membrane voltage
	i 	(nA)		: fluctuating current
	g_e	(umho)		: total excitatory conductance
	g_e1	(umho)		: fluctuating excitatory conductance
	D_e	(umho umho /ms) : excitatory diffusion coefficient
	exp_e
	amp_e	(umho)
        
        donotuse
}

STATE { O C D }

INITIAL {
	g_e1 = 0
	if(tau_e != 0) {
		D_e = 2 * std_e * std_e / tau_e
		exp_e = exp(-dt/tau_e)
		amp_e = std_e * sqrt( (1-exp(-2*dt/tau_e)) )
	}
        
        O = 0
        C = 1
        D = 0
}




BREAKPOINT {
        LOCAL SORN
	SOLVE oup
        SOLVE states METHOD derivimplicit
        
	if(tau_e==0) {
	   g_e = std_e * normrand123()
	}

        SORN = O * (1-D)
        
        g_e = g_e1 + SORN * cc_peak * g_e_max + g_e_baseline
          

        if(g_e < 0) {
            g_e = 0
        }

        i = g_e * (v - E_e)
}
DERIVATIVE states {
  LOCAL KO, KC1, KC2, KD1, KD2
  KO = 1/100
  KC1 = 1/100
  KC2 = 1e-4
  KD1 = 1/6000
  KD2 = 1/100
  O' = KO*(1-C-O)
  C' = KC1*(1-C)*C + KC2*(1-C)
  D' = KD1*O*(1-D) - KD2*D*(1-O)
}

PROCEDURE oup() {		: use Scop function normrand(mean, std_dev)
   if(tau_e!=0) {
	g_e1 =  exp_e * g_e1 + amp_e * normrand123()
   }
}

NET_RECEIVE(dummy) {
  C = 0
}


VERBATIM
double nrn_random_pick(void* r);
void* nrn_random_arg(int argpos);
ENDVERBATIM

FUNCTION normrand123() {
VERBATIM
	if (_p_donotuse) {
		/*
		:Supports separate independent but reproducible streams for
		: each instance. However, the corresponding hoc Random
		: distribution MUST be set to Random.negexp(1)
		*/
		_lnormrand123= nrn_random_pick(_p_donotuse);
	}else{
		/* only can be used in main thread */
		if (_nt != nrn_threads) {
hoc_execerror("multithread random in NetStim"," only via hoc Random");
		}
ENDVERBATIM
		: the old standby. Cannot use if reproducible parallel sim
		: independent of nhost or which host this instance is on
		: is desired, since each instance on this cpu draws from
		: the same stream
		normrand123 = normrand(0,1)
VERBATIM
	}
ENDVERBATIM
}

PROCEDURE noiseFromRandom() {
VERBATIM
 {
	void** pv = (void**)(&_p_donotuse);
	if (ifarg(1)) {
		*pv = nrn_random_arg(1);
	}else{
		*pv = (void*)0;
	}
 }
ENDVERBATIM
}

