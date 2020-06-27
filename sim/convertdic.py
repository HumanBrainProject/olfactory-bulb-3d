import bindict
import params

def convert(filename1, filename2):
    old_gid_mgrs_begin=params.gid_granule_begin+params.Ngranule
    if old_gid_mgrs_begin % 2 != 0: old_gid_mgrs_begin += 1
        
    gid_dict = {}
    bindict.load(filename1)
    for gid, ci in bindict.gid_dict.items():
        gid_dict[gid+params.gid_mgrs_begin-old_gid_mgrs_begin] = ci
    bindict.gid_dict = gid_dict
    bindict.save(filename2)

convert('fullbulb0-v3.dic', 'fullbulb0-v4.dic')
print '%0'

convert('fullbulb50-v3.dic', 'fullbulb50-v4.dic')
print '%50'

convert('fullbulb100-v3.dic', 'fullbulb100-v4.dic')
print '%100'

