from ADQ_tools_lite import sdr14
import numpy as np
import time
import sys

# Connect to SDR-14
try:
    device = sdr14()
except Exception as ex:
    print("No device connected!")
    sys.exit()
# Define pulse widths [ns]
pulses = np.array([10, 20, 30, 40, 50, 100, 150, 200, 250, 500, 750, 1000]) * 1000
# Define reg
reg = 2

for p in pulses:

    # Write
    if not device.reg_write(reg, p):
        print("Write unsuccessful, exiting ...")
        break

    time.sleep(0.5)
    # Enable/disable
    device.enable_dev()
    print("Device enabled!")
    time.sleep(8)
    device.disable_dev()
    print("Device disabled!")
    time.sleep(0.5)
    print("--------")

print("Finished!")