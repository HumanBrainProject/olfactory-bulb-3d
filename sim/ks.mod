TITLE K slow channel from Wang (2002)
: M.Migliore Dec. 2003

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)

}

PARAMETER {
	v (mV)
	celsius		(degC)
	gksbar=.005 (mho/cm2)
	q10=2
	ek

	
	:vhalfp=-34
        vhalfp=-35
	:tp=10
        tp=6	
	:kp=6.5
	kp=2

        :vhalfq =-65
        vhalfq=-50
        kq =6.6
	:to =200
        to=10
	tk =6.85  :6.8
	:a0q=220
        a0q=100

        :tvh=-71.6
        tvh=-50
        

}


NEURON {
	SUFFIX ks
	USEION k READ ek WRITE ik
        RANGE gksbar,gks
        GLOBAL pinf,qinf,taup,tauq
}

STATE {
	p
	q
}

ASSIGNED {
	ik (mA/cm2)
        pinf
        qinf      
        taup
        tauq
        gks
}

INITIAL {
	rates(v)
	p=pinf
	q=qinf
}


BREAKPOINT {
	SOLVE states METHOD cnexp
	gks = gksbar*p*q
	ik = gks*(v-ek)

}

DERIVATIVE states {     : exact when v held constant; integrates over dt step
        rates(v)
        p' = (pinf - p)/taup
        q' = (qinf - q)/tauq
}

PROCEDURE rates(v (mV)) { :callable from hoc
        LOCAL qt
        qt=q10^((celsius-25)/10)
        pinf = (1/(1+ exp(-(v-vhalfp)/kp)))
        qinf = (1/(1+ exp((v-vhalfq)/kq)))
	taup = tp/qt
	tauq = to + a0q/(1+exp(-(v-tvh)/tk))/qt
}






