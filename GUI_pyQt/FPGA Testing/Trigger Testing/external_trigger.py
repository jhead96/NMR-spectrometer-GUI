from ADQ_tools_lite import sdr14
import sys
import matplotlib.pyplot as plt
import numpy as np
import scipy.fft
import time
import ctypes as ct

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
f = 2 * 1000 * 1000
P1 = 20 * 1000
P2 = 10 * 1000
G1 = 20 * 1000
rec = 10 * 1000

device.reg_write(f_reg, f)
device.reg_write(P1_reg, P1)
device.reg_write(P2_reg, P2)
device.reg_write(G1_reg, G1)
device.reg_write(rec_reg, rec)

# Get device info
cu = device.cu
dev_number = device.device_number
api = device.api

# Set up trigger
device.set_clock_source()
device.set_MR_settings()
device.set_trigger_mode("EXTERNAL")
if api.ADQ_SetExternTrigEdge(cu, dev_number, 1):
    print("Trigger set to rising edge")

print(f"Waiting for trigger = {api.ADQ_GetWaitingForTrigger(cu, dev_number)}")

# Arm trigger
if api.ADQ_ArmTrigger(cu, dev_number):
    print("Trigger armed")

print(f"Waiting for trigger = {api.ADQ_GetAcquired(cu, dev_number)}")
# Enable dev
device.enable_dev()
print(f"Waiting for trigger = {api.ADQ_GetAcquired(cu, dev_number)}")
device.disable_dev()

# Set up buffers for data
max_channels = 2
target_buffers = (ct.POINTER(
    ct.c_int16 * device.stream_cfg_data.samples_per_record * device.stream_cfg_data.num_of_records) * max_channels)()

for buf_pntr in target_buffers:
    buf_pntr.contents = (
            ct.c_int16 * device.stream_cfg_data.samples_per_record * device.stream_cfg_data.num_of_records)()

# Get data from ADQ
ADQ_TRANSFER_MODE = 0  # Default mode
ADQ_CHANNELS_MASK = 0x3  # Read from both channels

status = api.ADQ_GetData(cu, dev_number, target_buffers,
                                device.stream_cfg_data.samples_per_record * device.stream_cfg_data.num_of_records,
                                2, 0, device.stream_cfg_data.num_of_records, ADQ_CHANNELS_MASK,
                                0, device.stream_cfg_data.samples_per_record, ADQ_TRANSFER_MODE)
if status:
    print('Data retrieved successfully')

ch1 = np.frombuffer(target_buffers[0].contents[0], dtype=np.int16)
ch2= np.frombuffer(target_buffers[1].contents[0], dtype=np.int16)

# Disarm trigger and close MR mode
api.ADQ_DisarmTrigger(cu, dev_number)
api.ADQ_MultiRecordClose(cu, dev_number)

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

plt.figure()
plt.plot(ch1)
plt.plot(ch2)

#np.savetxt("1MHZ_trigger_test", np.array([t, ch1, ch2]))
