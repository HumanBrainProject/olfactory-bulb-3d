from misc import *
import copy
__somar = [ [], [], [], [], [] ]
__somar[0] += [ [ -4.64988, -5.20346, 19.2301, 3.72505 ] ]
__somar[0] += [ [ -3.84717, -5.25629, 17.2755, 6.64771 ] ]
__somar[0] += [ [ -3.04446, -5.30912, 15.3209, 12.492 ] ]
__somar[0] += [ [ -2.24176, -5.36195, 13.3662, 17.2341 ] ]
__somar[0] += [ [ -1.43905, -5.41478, 11.4116, 20.3893 ] ]
__somar[0] += [ [ -0.636342, -5.4676, 9.45701, 23.5446 ] ]
__somar[0] += [ [ 0.166365, -5.52043, 7.50239, 25.5399 ] ]
__somar[0] += [ [ 0.969072, -5.57326, 5.54777, 27.321 ] ]
__somar[0] += [ [ 1.77178, -5.62609, 3.59315, 28.4545 ] ]
__somar[0] += [ [ 2.57449, -5.67892, 1.63853, 28.5444 ] ]
__somar[0] += [ [ 3.37719, -5.73175, -0.316091, 28.6342 ] ]
__somar[0] += [ [ 4.1799, -5.78458, -2.27071, 28.7241 ] ]
__somar[0] += [ [ 4.98261, -5.8374, -4.22533, 28.8139 ] ]
__somar[0] += [ [ 5.78532, -5.89023, -6.17995, 28.7778 ] ]
__somar[0] += [ [ 6.58802, -5.94306, -8.13457, 27.5509 ] ]
__somar[0] += [ [ 7.39073, -5.99589, -10.0892, 24.662 ] ]
__somar[0] += [ [ 8.19344, -6.04872, -12.0438, 21.7659 ] ]
__somar[0] += [ [ 8.99615, -6.10155, -13.9984, 18.8697 ] ]
__somar[0] += [ [ 9.79885, -6.15438, -15.9531, 15.9736 ] ]
__somar[0] += [ [ 10.6016, -6.2072, -17.9077, 12.8157 ] ]
__somar[0] += [ [ 11.4043, -6.26003, -19.8623, 7.15979 ] ]
__somar[1] += [ [ -6.09478, -0.258876, 17.4299, 3.49374 ] ]
__somar[1] += [ [ -5.25081, -0.282379, 16.3378, 5.90019 ] ]
__somar[1] += [ [ -4.40684, -0.305882, 15.2456, 9.07648 ] ]
__somar[1] += [ [ -3.56287, -0.329384, 14.1535, 11.2008 ] ]
__somar[1] += [ [ -2.7189, -0.352887, 13.0614, 13.4637 ] ]
__somar[1] += [ [ -1.87493, -0.37639, 11.9692, 14.2691 ] ]
__somar[1] += [ [ -1.03096, -0.399893, 10.8771, 15.0652 ] ]
__somar[1] += [ [ -0.18699, -0.423396, 9.78496, 15.3968 ] ]
__somar[1] += [ [ 0.656979, -0.446899, 8.69283, 15.3743 ] ]
__somar[1] += [ [ 1.50095, -0.470402, 7.60069, 15.3519 ] ]
__somar[1] += [ [ 2.34492, -0.493905, 6.50856, 15.3292 ] ]
__somar[1] += [ [ 3.18889, -0.517408, 5.41643, 15.2902 ] ]
__somar[1] += [ [ 4.03286, -0.540911, 4.32429, 15.2423 ] ]
__somar[1] += [ [ 4.87683, -0.564414, 3.23216, 15.0648 ] ]
__somar[1] += [ [ 5.72079, -0.587917, 2.14003, 14.7259 ] ]
__somar[1] += [ [ 6.56476, -0.61142, 1.04789, 14.3006 ] ]
__somar[1] += [ [ 7.40873, -0.634923, -0.0442405, 13.2035 ] ]
__somar[1] += [ [ 8.2527, -0.658426, -1.13637, 11.9114 ] ]
__somar[1] += [ [ 9.09667, -0.681929, -2.22851, 9.90796 ] ]
__somar[1] += [ [ 9.94064, -0.705432, -3.32064, 6.99624 ] ]
__somar[1] += [ [ 10.7846, -0.728935, -4.41277, 4.04732 ] ]
__somar[2] += [ [ -6.09478, -0.258876, 17.4299, 3.49374 ] ]
__somar[2] += [ [ -5.25081, -0.282379, 16.3378, 5.90019 ] ]
__somar[2] += [ [ -4.40684, -0.305882, 15.2456, 9.07648 ] ]
__somar[2] += [ [ -3.56287, -0.329384, 14.1535, 11.2008 ] ]
__somar[2] += [ [ -2.7189, -0.352887, 13.0614, 13.4637 ] ]
__somar[2] += [ [ -1.87493, -0.37639, 11.9692, 14.2691 ] ]
__somar[2] += [ [ -1.03096, -0.399893, 10.8771, 15.0652 ] ]
__somar[2] += [ [ -0.18699, -0.423396, 9.78496, 15.3968 ] ]
__somar[2] += [ [ 0.656979, -0.446899, 8.69283, 15.3743 ] ]
__somar[2] += [ [ 1.50095, -0.470402, 7.60069, 15.3519 ] ]
__somar[2] += [ [ 2.34492, -0.493905, 6.50856, 15.3292 ] ]
__somar[2] += [ [ 3.18889, -0.517408, 5.41643, 15.2902 ] ]
__somar[2] += [ [ 4.03286, -0.540911, 4.32429, 15.2423 ] ]
__somar[2] += [ [ 4.87683, -0.564414, 3.23216, 15.0648 ] ]
__somar[2] += [ [ 5.72079, -0.587917, 2.14003, 14.7259 ] ]
__somar[2] += [ [ 6.56476, -0.61142, 1.04789, 14.3006 ] ]
__somar[2] += [ [ 7.40873, -0.634923, -0.0442405, 13.2035 ] ]
__somar[2] += [ [ 8.2527, -0.658426, -1.13637, 11.9114 ] ]
__somar[2] += [ [ 9.09667, -0.681929, -2.22851, 9.90796 ] ]
__somar[2] += [ [ 9.94064, -0.705432, -3.32064, 6.99624 ] ]
__somar[2] += [ [ 10.7846, -0.728935, -4.41277, 4.04732 ] ]
__somar[3] += [ [ -2.23481, -53.7362, 14.2419, 2.99861 ] ]
__somar[3] += [ [ -1.76314, -53.8338, 12.9902, 5.47905 ] ]
__somar[3] += [ [ -1.29148, -53.9313, 11.7385, 7.98081 ] ]
__somar[3] += [ [ -0.819817, -54.0289, 10.4868, 10.0703 ] ]
__somar[3] += [ [ -0.348154, -54.1264, 9.2351, 11.4542 ] ]
__somar[3] += [ [ 0.12351, -54.2239, 7.9834, 12.3129 ] ]
__somar[3] += [ [ 0.595173, -54.3215, 6.7317, 13.3961 ] ]
__somar[3] += [ [ 1.06684, -54.419, 5.48, 16.5383 ] ]
__somar[3] += [ [ 1.5385, -54.5166, 4.22831, 19.1186 ] ]
__somar[3] += [ [ 2.01016, -54.6141, 2.97661, 19.7045 ] ]
__somar[3] += [ [ 2.48183, -54.7117, 1.72491, 20.2903 ] ]
__somar[3] += [ [ 2.95349, -54.8092, 0.473214, 20.0805 ] ]
__somar[3] += [ [ 3.42515, -54.9068, -0.778484, 19.6602 ] ]
__somar[3] += [ [ 3.89682, -55.0043, -2.03018, 19.1795 ] ]
__somar[3] += [ [ 4.36848, -55.1019, -3.28188, 18.1662 ] ]
__somar[3] += [ [ 4.84014, -55.1994, -4.53358, 16.7538 ] ]
__somar[3] += [ [ 5.31181, -55.2969, -5.78527, 14.8449 ] ]
__somar[3] += [ [ 5.78347, -55.3945, -7.03697, 12.936 ] ]
__somar[3] += [ [ 6.25513, -55.492, -8.28867, 10.3131 ] ]
__somar[3] += [ [ 6.7268, -55.5896, -9.54037, 6.51347 ] ]
__somar[3] += [ [ 7.19846, -55.6871, -10.7921, 3.56534 ] ]
__somar[4] += [ [ -11.6624, -5.98159, 39.7401, 2.53773 ] ]
__somar[4] += [ [ -10.108, -5.84634, 38.8583, 3.66685 ] ]
__somar[4] += [ [ -8.55354, -5.7111, 37.9764, 5.31313 ] ]
__somar[4] += [ [ -6.99909, -5.57586, 37.0945, 6.31607 ] ]
__somar[4] += [ [ -5.44464, -5.44061, 36.2126, 7.29106 ] ]
__somar[4] += [ [ -3.89019, -5.30537, 35.3307, 8.08265 ] ]
__somar[4] += [ [ -2.33574, -5.17013, 34.4488, 8.85495 ] ]
__somar[4] += [ [ -0.781296, -5.03489, 33.567, 9.49124 ] ]
__somar[4] += [ [ 0.773151, -4.89964, 32.6851, 9.94162 ] ]
__somar[4] += [ [ 2.3276, -4.7644, 31.8032, 10.3171 ] ]
__somar[4] += [ [ 3.88205, -4.62916, 30.9213, 10.4725 ] ]
__somar[4] += [ [ 5.43649, -4.49392, 30.0394, 10.5889 ] ]
__somar[4] += [ [ 6.99094, -4.35867, 29.1576, 10.7002 ] ]
__somar[4] += [ [ 8.54539, -4.22343, 28.2757, 10.8104 ] ]
__somar[4] += [ [ 10.0998, -4.08819, 27.3938, 10.7998 ] ]
__somar[4] += [ [ 11.6543, -3.95294, 26.5119, 10.6434 ] ]
__somar[4] += [ [ 13.2087, -3.8177, 25.63, 10.2144 ] ]
__somar[4] += [ [ 14.7632, -3.68246, 24.7481, 9.67498 ] ]
__somar[4] += [ [ 16.3176, -3.54722, 23.8663, 8.2052 ] ]
__somar[4] += [ [ 17.8721, -3.41197, 22.9844, 5.77718 ] ]
__somar[4] += [ [ 19.4265, -3.27673, 22.1025, 3.22379 ] ]

N_SOMA = len(__somar)

def realSoma(i, p):
    soma1 = copy.deepcopy(__somar[i])

    # translation vector calculation
    vec = centroid(soma1)
    for j in range(3): vec[j] = p[j] - vec[j]
    
    # translate
    for x in soma1:
        for j in range(3):
            x[j] += vec[j]

    return soma1
    
    
