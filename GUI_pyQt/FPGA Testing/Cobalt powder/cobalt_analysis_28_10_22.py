import numpy as np
import matplotlib.pyplot as plt
from analysis_functions import calculate_RFFT, generate_datafile_header, save_analyzed_data




N_files = 30
filenames = [f"Raw data\p2_1pt0us\cobalt_signal_p2_1us_{i}" for i in range(0, N_files)]

t = []
ch1 = []
ch2 = []
# Read data
for f in filenames:
    data = np.loadtxt(f)

    t.append(data[0, :])
    ch1.append(data[1, :])
    ch2.append(data[2, :])

t = np.array(t) / 1e-6
ch1 = np.array(ch1)
ch2 = np.array(ch2)

plt.plot(t[0, :], ch1[0, :])
plt.plot(t[0, :], ch2[0, :])


# Average signals
ch1_avg = np.mean(ch1, axis=0)
ch2_avg = np.mean(ch2, axis=0)

t_avg = t[0, :]

plt.figure()
plt.plot(t[0, :], ch1_avg, label="Ch1 (Real)")
plt.plot(t[0, :], ch2_avg, label="Ch2 (Im)")
plt.xlabel("t (us)")
plt.xlim(0, 1)
plt.legend()

plt.title("Averaged cobalt signal (f = 213MHz)")

FID_start = 0.391
# Get FID
ch1_FID = ch1_avg[t_avg > FID_start]
ch2_FID = ch2_avg[t_avg > FID_start]
t_FID = t_avg[t_avg > FID_start]

# Adjust zero point
t_FID = t_FID - t_FID[0]

plt.figure("Shifted FID")
plt.plot(t_FID, ch1_FID, label="Ch1 (Real)")
plt.plot(t_FID, ch2_FID, label="Ch2 (Im)")
plt.xlabel("t (us)")
plt.xlim(0, 1)
plt.legend()

# Cut samples
N_cut = 11
t_cut = t_FID[:+2**N_cut]
ch1_cut = ch1_FID[:+2**N_cut]
ch2_cut = ch2_FID[:+2**N_cut]

plt.figure()
plt.plot(t_cut, ch1_cut, label="Ch1 (Real)")
plt.plot(t_cut, ch2_cut, label="Ch2 (Im)")
plt.xlabel("t (us)")
plt.title(f"FID (N = {2**N_cut} points)")
plt.legend()

#header = generate_datafile_header(f_MHz=213, p1_us=1, p2_us=2, g1_us=20, N_scans=30, atten_dB=20)
#save_analyzed_data((t_cut, ch1_cut, ch2_cut), filepath=r"Processed data\First cobalt signal.txt", header=header)
