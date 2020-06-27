


# synapses conductances
mc_exc_gmax = 1.25  # nS
mc_inh_gmax = 0.018 # uS

mt_exc_gmax = 1.25  # nS
mt_inh_gmax = 0.018 # uS

mt2bc_exc_gmax=0.25e-4
bc2gc_inh_gmax=0.5

# stream sniff
# you must change this to change the stimulation sequence
# of tuft weights or sniffs activation times
stream_ods_shift = 1

# odorsequence
# for each odor you must add a tuple in this manner
# the possible odors name are
# 'Apple', 'Banana', 'Basil', 'Black_Pepper',
# 'Cheese', 'Chocolate', 'Cinnamon',
# 'Cloves', 'Coffee', 'Garlic', 'Ginger',
# 'Lemongrass', 'Kiwi', 'Mint', 'Onion',
# 'Oregano', 'Pear', 'Pineapple'

# ('Mint', t init, t duration, rel. conc.), (...), (...)
odor_sequence = [ ]

# segments to records
# (cell gid, section index, arc, output filename)
sec2rec = []
#sec2rec += [  (x, None, None) for x in (range(185,190)+range(1005, 1015)) ]
#sec2rec += [  (x, None, None) for x in (range(160,165)+range(955, 965)) ]
#sec2rec += [  (x, None, None) for x in (range(390,395)+range(1415, 1425)) ]

# sim. duration
tstop = 5050

initial_weights = '' 

# dummy syns parameters
dummy_syn_conn = ''#dummysyns.txt'
ndummy_syn = 46

# sniff interval
# None is random
# the number was constant
sniff_invl_min = 350
sniff_invl_max = 350

init_exc_weight = 75/2
init_inh_weight = 50/2

training_exc = False
training_inh = False

glom2blanes = []
