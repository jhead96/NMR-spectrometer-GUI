import numpy as np



s1 = "00000000"
s2 = "00001111"
s3 = "11110000"
s4 = "11111111"

s = np.array([s1+s2+s3+s4, s1+s2+s3+s4])

t = split_simulation_output(s)