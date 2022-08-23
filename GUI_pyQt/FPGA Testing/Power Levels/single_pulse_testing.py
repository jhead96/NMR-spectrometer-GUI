import ADQ_tools_lite
import numpy as np
import time
import sys

# Connect to SDR-14
try:
    device = ADQ_tools_lite.sdr14()
except Exception as ex:
    print("No device connected!")
    sys.exit()

# Define pulse widths [ns]
pulses = np.arange(10, 110, 10, dtype=int) * 1e3
# Define reg
reg = 2

for p in pulses:

    # Write
    if device.reg_write(reg, p):
        print(f"Write successful")
    else:
        print("Write unsuccessful, exiting ...")
        break

    # Read
    if device.reg_read(reg) == p:
        print(f"Reg value = {p} ns")
    else:
        print("Read failed, exiting ...")
        break

    time.sleep(1)
    # Enable/disable
    device.enable_dev()
    print("Device enabled!")
    time.sleep(5)
    device.disable_dev()
    print("Device disabled!")
    time.sleep(1)
    print("--------")











