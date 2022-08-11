from scope_reader import ScopeReader
import numpy as np
import matplotlib.pyplot as plt

def Vpp_to_P(Vpp):

    R = 50
    Vrms = Vpp / np.sqrt(2)
    P_W = (Vrms ** 2) / R
    P_dBm = 10 * np.log10(P_W * 1e3)

    return np.array([P_W, P_dBm])

R = 50

freqs = ["0pt5", 1, 10, 100, 200, 300, 400, 500, 600, 700, 800]
freqs2 = [0.5, 1, 10, 100, 200, 300, 400, 500, 600, 700, 800]

filenames = ["FPGA_output_" + str(i) + "MHz.csv" for i in freqs]
data = []

for f in filenames:
    data.append(ScopeReader(f))

Vpp = []
Vpp_from_spectrum = []

for ds in data:
    ds.plot_data()
    Vpp.append(ds.amp)

    # Calculate power from spectrum
    Vrms = np.sqrt(ds.power*R)
    Vpp_from_spectrum.append(np.sqrt(2)*Vrms)

Vpp = np.array(Vpp)
Vpp_from_spectrum = np.array(Vpp_from_spectrum)

P = Vpp_to_P(Vpp)
P_from_spectrum = Vpp_to_P(Vpp_from_spectrum)


fig1, ax1 = plt.subplots()
ax1.plot(freqs2, Vpp, "r.-", label="Calculated from $V(t)$")
ax1.plot(freqs2, Vpp_from_spectrum, "b.-", label="Calculated from PSD")
ax1.set_title("FPGA output $V_{pp}$ as a function of frequency")
ax1.set_xlabel("$f$ (MHz)")
ax1.set_ylabel("$V_{pp}$ (V)")
ax1.legend()


fig2, ax1 = plt.subplots()
ax1.plot(freqs2, P[1,:], "r.-", label="Calculated from $V(t)$")
ax1.plot(freqs2, P_from_spectrum[1,:], "b.-", label="Calculated from PSD")
ax1.set_title("FPGA output power as a function of frequency")
ax1.set_xlabel("$f$ (MHz)")
ax1.set_ylabel("$P$ (dBm)")
ax1.legend()



