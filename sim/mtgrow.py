import params
import MTrealSoma as realSoma
#import MCrealSoma as realSoma

somaAxisUp = [ 2100.0-100, 2800.0-100, 2100.0-100]
somaAxisDw = [ x-100 for x in somaAxisUp ]

 
from math import pi, exp
# specific grow parameters

GROW_MAX_ITERATIONS = 2000
GROW_MAX_ATTEMPTS = 100

## apical params
APIC_DIAM = 4 # modified from Francesco's value
APIC_LEN_MAX = 350.-150

## tuft params
## tuft params
TUFT_DIAM = 0.8 # modified from Francesco's value
N_MIN_TUFT = 5
N_MAX_TUFT = 5
TUFT_MIN_LEN = 40
TUFT_MAX_LEN = 80


# dendrites definition
N_MIN_DEND = 2
N_MAX_DEND = 6
N_MEAN_DEND = 3

# dendrites max length, normal distribution
DEND_LEN_MU =  654.47
DEND_LEN_VAR = 286.43 ** 2
DEND_LEN_MIN = 50.
DEND_LEN_MAX = 1260.0

# dendrites bifurcation parameters, exponential distribution
branch_len_mean = [ 23.3, 53.3, 142, 180, 306.7, 106.7 ]
branch_len_min = [ 20, 20, 20, 20, 20, 2 ]
branch_len_max = [ 100, 260, 380, 520, 560, 240 ]
branch_prob = [ 0.9, 0.71, 0.63, 0.58, 0.25, 0.13 ]



## random walk, noise
GRW_WALK_LEN = 20.
BIFURC_PHI_MU = 0.5
BIFURC_PHI_MIN = pi / 24.
BIFURC_PHI_MAX = pi / 5.
NS_PHI_B = 0.15
NS_PHI_MIN = -6.
NS_PHI_MAX = 6.
NS_THETA_B = 0.15
NS_THETA_MIN = -1.2
NS_THETA_MAX = 1.2

GROW_RESISTANCE = 1.5


# glomerulus radius

GLOM_DIST =  25

init_theta = pi / 2

diam_min_dend = 2.25
diam_max_dend = 2.75
diam_tape_dend = 0.0013*4/3
