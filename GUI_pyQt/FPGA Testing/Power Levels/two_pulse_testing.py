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
P1 = np.array([10, 20, 30, 40, 50, 100, 150, 200, 250, 500, 750, 1000]) * 1000
# Define regs
P1_reg = 2
P2_reg = 3
G1_reg = 4

# Test one pulse
"""for p in P1:

    # Write
    if not device.reg_write(P1_reg, p):
        print("Write unsuccessful, exiting ...")
        break

    time.sleep(0.5)
    # Enable/disable
    device.enable_dev()
    print("Device enabled!")
    #time.sleep(8)
    device.disable_dev()
    print("Device disabled!")
    time.sleep(0.5)
    print("--------")

print("Single pulse tests complete!")
input("Press any key to continue...")"""

# Test two pulses
P1 = 20 * 1000
P2 = 10 * 1000
G1 = 20 * 1000

device.reg_write(P1_reg, P1)
device.reg_write(P2_reg, P2)
device.reg_write(G1_reg, G1)

for i in range(3):
    device.enable_dev()
    time.sleep(5)
    device.disable_dev()
    time.sleep(5)
print("Finished!")


