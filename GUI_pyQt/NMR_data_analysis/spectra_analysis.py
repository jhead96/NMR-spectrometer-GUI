import numpy as np
import matplotlib.pyplot as plt

# Read processed files
dirpath = r"X:\chungm-quantum-magnetism\PhD projects\Jake Head\NMR Data\Cobalt Powder\spectrum_processed_data\\"
freqs = np.arange(213, 220, 0.5)
filenames = [f"{str(f).replace('.','pt')}_MHz_processed.txt" for f in freqs]
n_data = 65536
n_files = len(filenames)
header_size = 10

data = np.zeros((n_data, 3, n_files))

for i, f in enumerate(filenames):
    data[:, :, i] = np.loadtxt(dirpath + f, skiprows=header_size)

t = data[:, 0, 0]
Mx = data[:, 1, 0]
My = data[:, 2, 0]
mag = ((Mx**2) + (My**2)) ** 0.5

fig1, fig1_ax1 = plt.subplots()

fig1_ax1.plot(t, Mx, label="Mx")
fig1_ax1.plot(t, My, label="My")
fig1_ax1.plot(t, mag, label="Magnitude")
fig1_ax1.set_title("213MHz signal, P1=2us, G1=10us, P2=4us")
fig1_ax1.set_xlabel("t (us)")
fig1_ax1.set_ylabel("Signal")
fig1_ax1.set_xlim(0, 20)
fig1_ax1.set_ylim(-100,100)
fig1.legend()




