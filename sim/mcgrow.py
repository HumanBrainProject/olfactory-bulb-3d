import params
import MCrealSoma as realSoma

somaAxisUp = [ params.bulbAxis[i]-600 for i in range(3) ]
somaAxisDw = [ params.bulbAxis[i]-700 for i in range(3) ]
            

from math import pi, exp
# specific grow parameters

GROW_MAX_ITERATIONS = 2000
GROW_MAX_ATTEMPTS = 100

##### ATTENTION: parameters may change in the future

## apical params
APIC_DIAM = 4 # modified from Francesco's value
APIC_LEN_MAX = 550.-150

## tuft params
N_MIN_TUFT = 5
N_MAX_TUFT = 5
TUFT_DIAM = 0.8
TUFT_MIN_LEN = 40
TUFT_MAX_LEN = 80

# dendrites paramaters
#N_MIN_DEND = 4
#N_MAX_DEND = 6
#DEND_DIAM = 2

# dendrites definition
N_MIN_DEND = 4
N_MAX_DEND = 9
N_MEAN_DEND = 5

# dendrites max length, normal distribution
DEND_LEN_MU = 837.97
DEND_LEN_VAR = 283.04 ** 2
DEND_LEN_MIN = 50.
DEND_LEN_MAX = 1800.

# dendrites bifurcation parameters, exponential distribution
branch_len_mean = [ 85.32, 226.61, 226.61, 226.61, 226.61 ]
branch_len_min = [ 2.95, 0.5, 0.5, 0.5, 0.5 ]
branch_len_max = [ 325.0, 825.0,  825.0,  825.0,  825.0 ]
branch_prob = [ 0.75, 0.63, 0.42, 0.28, 0.06 ]


def gen_dend_diam(dist): return 0.9 + 2.6 * exp(-0.0013 * dist) #value's estimated with a fitting

## random walk, noise
GRW_WALK_LEN = 20.
BIFURC_PHI_MU = 0.5
BIFURC_PHI_MIN = pi / 24.
BIFURC_PHI_MAX = pi / 5.
NS_PHI_B = 0.16
NS_PHI_MIN = -6.26
NS_PHI_MAX = 6.26
NS_THETA_B = 0.1407
NS_THETA_MIN = -1.56
NS_THETA_MAX = 1.18

GROW_RESISTANCE = 1.5

# glomerulus radius

GLOM_DIST = 10. #50.

init_theta = pi / 3

diam_min_dend = 2.25
diam_max_dend = 2.75
diam_tape_dend = 0.0013
