from ADQ_tools_lite import sdr14
import sys
import matplotlib.pyplot as plt
import numpy as np
import scipy.fft

# Connect to SDR-14
try:
    device = sdr14()
except Exception as ex:
    print("No device connected!")
    sys.exit()

# Define regs
f_reg = 1
P1_reg = 2
P2_reg = 3
G1_reg = 5
rec_reg = 7

# Set up two pulse sequence
f = 50 * 1000 * 1000
P1 = 20 * 1000
P2 = 10 * 1000
G1 = 20 * 1000
rec = 10 * 1000

device.reg_write(f_reg, f)
device.reg_write(P1_reg, P1)
device.reg_write(P2_reg, P2)
device.reg_write(G1_reg, G1)
device.reg_write(rec_reg, rec)


# Enable dev
device.enable_dev()
ch1, ch2 = device.MR_acquisition(1)
device.disable_dev()




# Calculate t axis
N = ch1.size
fs = 800e6
Ts = 1/fs
t = np.arange(0, N*Ts, Ts)

# FFT
yf = np.abs(scipy.fft.rfft(ch1))
xf = scipy.fft.rfftfreq(N, d=Ts)

plt.plot(t/1e-6, ch1)
plt.xlabel("t (us)")

plt.figure()
plt.plot(xf/1e6, yf)

plt.xlabel("f (MHz)")

