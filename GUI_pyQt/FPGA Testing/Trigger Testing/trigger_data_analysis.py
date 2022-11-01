from analysis_functions import calculate_RFFT
from scope_readers import GwInstekReader
import numpy as np
import matplotlib.pyplot as plt

# Read scope data
filepaths = np.array([r"test_data\A0014CH1.CSV", r"test_data\A0014CH2.CSV"])

data = {'Function generator': GwInstekReader(filepaths[1]), 'FPGA trigger': GwInstekReader(filepaths[0])}

for key, ds in data.items():
    plt.plot(ds.t/1e-6, ds.y, label=f"{key} signal")

plt.title("Scope output triggered using FPGA generated trigger")
plt.xlabel("t (us)")
plt.ylabel("Signal")
plt.legend()

# Read FPGA data
t, ch1, ch2 = np.loadtxt(r"test_data/1MHZ_trigger_test")


plt.figure()
plt.plot(t/1e-6, ch1, label="Ch 1")
plt.plot(t/1e-6, ch2, label="Ch 2")

plt.title("FPGA output using FPGA generated trigger")
plt.xlabel("t (us)")
plt.ylabel("Signal")
plt.legend()

# Combined plot
plt.figure()
for key, ds in data.items():
    print(key)
    plt.plot((ds.t/1e-6)-79, ds.y, label=f"{key} signal")

plt.legend()

sf = 0.001
offset = 10



scope_trigger = 0.96 # Scope trigger time [us]
fg_start = 1.23 # function generator signal start time [us]
lag = fg_start - scope_trigger

plt.vlines(scope_trigger, 0, 4, linestyles="dashed", label="Scope trigger (Level = 0.64V)")
plt.vlines(1.23, 0, 4, colors="r", linestyles="dashed", label="Function generator signal start")


print(f"Scope triggered at {scope_trigger} us")
print(f"Function generator output detected at {fg_start} us")
print(f"Delay = {lag} us")

plt.plot((t/1e-6) - lag, sf*ch1 + offset, label="Ch 1 - FPGA (Adjusted by delay)")
plt.plot((t/1e-6) - lag, sf*ch2 + offset, label="Ch 2 - FPGA (Adjusted by delay)")
plt.xlim(0, 18)
plt.xlabel("t (us)")
plt.ylabel("Signal")
plt.legend()
