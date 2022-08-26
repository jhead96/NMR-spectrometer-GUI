from ADQ_tools_lite import sdr14
import numpy as np
import time

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
G1_reg = 5

# Test one pulse
for p in P1:

    # Write
    if not device.reg_write(P1_reg, p):
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

print("One pulse tests complete!")
input("Press any key to continue...")

# Test two pulses



