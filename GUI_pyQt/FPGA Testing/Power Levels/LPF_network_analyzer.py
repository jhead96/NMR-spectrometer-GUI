import numpy as np
import matplotlib.pyplot as plt

filepath = r"HP_8720D_network_analyzer_data/VLF800_frqrsp.CSV"

data = np.genfromtxt(filepath, delimiter=",", skip_header=12)

plt.plot(data[:, 0] / 1e9, data[:, 1])
plt.title("VLF 800+ frequency response")
plt.xlabel("f (GHz)")
plt.ylabel("Gain (dB)")
