from scope_reader import ScopeReader
import numpy as np
import matplotlib.pyplot as plt

freqs = ["0pt5", 1, 10, 100, 200, 300, 400]
freqs2 = [0.5, 1, 10, 100, 200, 300, 400]

filenames = ["FPGA_output_" + str(i) + "MHz.csv" for i in freqs]
data = []

for f in filenames:
    data.append(ScopeReader(f))

Vpp = []

for ds in data:
    ds.plot_data()
    Vpp.append(ds.amp)

fig1, ax1 = plt.subplots()
ax1.plot(freqs2, Vpp, ".-")
ax1.set_title("FPGA output $V_{pp}$ as a function of frequency")
ax1.set_xlabel("$f$ (MHz)")
ax1.set_ylabel("$V_{pp}$ (V)")
