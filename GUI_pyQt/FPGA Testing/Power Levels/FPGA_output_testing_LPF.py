from scope_readers import TektronixReader
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal


R = 50

freqs = [1, 10, 100, 200, 300, 400, 500, 600, 700, 800]

filenames = [r"FPGA_output_test_data/LPF/FPGA_output_" + str(i) + "MHz.csv" for i in freqs]
data = []

for f in filenames:
    data.append(TektronixReader(f))

for ds in data:
    ds.plot_PSD()