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

# Calculate magnitude
Mx_sq = data[:, 1, :] ** 2
My_sq = data[:, 2, :] ** 2
mag = (Mx_sq + My_sq) ** 0.5

data = np.hstack((data, mag[:, None, :]))

fig1, fig1_ax1 = plt.subplots()
for i in range(0, n_files):
    fig1_ax1.plot(data[:, 0, i], data[:, 3, i], label=f"f = {freqs[i]}")
fig1_ax1.set_title("P1=4us, G1=10us, P2=2us")
fig1_ax1.set_xlabel("t (us)")
fig1_ax1.set_ylabel("Signal")
fig1_ax1.set_xlim(0, 20)
fig1_ax1.set_ylim(-100,100)
fig1.legend()
plt.show()




