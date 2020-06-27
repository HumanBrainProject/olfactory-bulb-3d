NEURON {
    POINT_PROCESS Gap
    ELECTRODE_CURRENT i
    RANGE g, i, vgap
    THREADSAFE
}

PARAMETER {
    g = 4 (nanosiemens)
}

ASSIGNED {
    vgap (millivolt)
    i (nanoamp)
    v (millivolt) 
}



BREAKPOINT {
    i = g * (vgap - v) * 1e-3
}

