from scope_reader import ScopeReader
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal

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
    ds.plot_PSD()
    Vpp.append(ds.amp)

    # Calculate power from spectrum
    Vrms = np.sqrt(ds.power*R)
    Vpp_from_spectrum.append(np.sqrt(2)*Vrms)

Vpp = np.array(Vpp)
Vpp_from_spectrum = np.array(Vpp_from_spectrum)

P = Vpp_to_P(Vpp)
P_from_spectrum = Vpp_to_P(Vpp_from_spectrum)

# Plot voltages
fig1, ax1 = plt.subplots()
ax1.plot(freqs2, Vpp, "r.-", label="Calculated from $V(t)$")
ax1.plot(freqs2, Vpp_from_spectrum, "b.-", label="Calculated from PSD")
ax1.set_title("FPGA output $V_{pp}$ as a function of frequency")
ax1.set_xlabel("$f$ (MHz)")
ax1.set_ylabel("$V_{pp}$ (V)")
ax1.legend()

# Plot power
fig2, ax1 = plt.subplots()
ax1.plot(freqs2, P[1,:], "r.-", label="Calculated from $V(t)$")
ax1.plot(freqs2, P_from_spectrum[1,:], "b.-", label="Calculated from PSD")
ax1.set_title("FPGA output power as a function of frequency")
ax1.set_xlabel("$f$ (MHz)")
ax1.set_ylabel("$P$ (dBm)")
ax1.legend()


high_freqs = np.array(freqs2[3:])
high_freq_data = np.array(data[3:])
pks_index = np.zeros((7, high_freqs.shape[0]))
pks_freq = np.zeros((7, high_freqs.shape[0]))




num_pks = []

for i in range(high_freqs.shape[0]):
    # Find peaks
    pks = scipy.signal.find_peaks(high_freq_data[i].PSD, height=2e-10)[0]
    num = pks.shape[0]
    num_pks.append(num)
    pks_index[0:num, i] = pks.astype(int)
    # Convert peak index -> f = index * (fs/N)
    pks_freq[0:num, i] = pks_index[0:num, i] * (high_freq_data[i].fs / high_freq_data[i].N)

# Generate 2D arrays for plotting
f_out = np.zeros(pks_freq.shape)
f_out[f_out + pks_freq != 0] = 1
f_out = f_out * high_freqs[None, :]

# Plot theory lines
fs_FPGA = 1.6e9
x_theory = np.linspace(0,800, 100)
y_lower = fs_FPGA - x_theory*1e6
y_upper = fs_FPGA + x_theory*1e6


# Plot
fig3, fig3_ax1 = plt.subplots()

f_out[f_out == 0] = np.nan

fig3_ax1.plot(x_theory, y_lower/1e6, "r--", label="$f_{s,FPGA} \\pm f_{out}$")
fig3_ax1.plot(x_theory, y_upper/1e6, "r--")
fig3_ax1.hlines(fs_FPGA/1e6, 0, 800, colors="k", linestyle="dashed", label="$f_{s,FPGA}$")
fig3_ax1.scatter(f_out[0,:], pks_freq[0,:]/1e6, c="b", label="Dominant peaks in PSD")
fig3_ax1.scatter(f_out, pks_freq/1e6, c="g", label="Secondary Peaks in PSD", zorder=-5)


fig3_ax1.set_xlabel("$f_{out}$ (MHz)")
fig3_ax1.set_ylabel("$f_{peaks}$ (MHZ)")
fig3_ax1.set_title("Frequency components for a generated FPGA signal, $f_{out}$")
fig3_ax1.set_ylim(0, 2.5e3)
fig3_ax1.legend()






