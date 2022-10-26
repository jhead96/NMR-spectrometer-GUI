import numpy as np
import matplotlib.pyplot as plt

filepath = r"HP_8720D_network_analyzer_data/VLF800_frqrsp_0dBm.CSV"

data = np.genfromtxt(filepath, delimiter=",", skip_header=12)

plt.plot(data[:, 0] / 1e9, data[:, 1], "b:", label="0 dBm", zorder=10)


filepath = r"HP_8720D_network_analyzer_data/VLF800_frqrsp_-4dBm.CSV"

data = np.genfromtxt(filepath, delimiter=",", skip_header=12)

plt.plot(data[:, 0] / 1e9, data[:, 1], 'r', label="-4 dBm")
plt.hlines(-3, 0, 1.5, color="k", linestyle="dashed", label="-3dB line")
plt.title("VLF 800+ frequency response")
plt.xlabel("f (GHz)")
plt.ylabel("Gain (dB)")
plt.legend(title="Input power")