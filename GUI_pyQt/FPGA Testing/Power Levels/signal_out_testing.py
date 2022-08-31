from ADQ_tools_lite import sdr14
import numpy as np
import sys
import time

def test_signal_out():
    """
    Function for generating a set of signal out test data at a number of frequencies.
    """

    freqs = np.array([1, 10, 100, 200, 300, 400, 500, 600, 700, 800]) * 1000000
    reg = 1

    for f in freqs:
        # Write
        if not device.reg_write(reg, f):
            print("Write unsuccessful, exiting ...")
            break

        time.sleep(0.5)
        # Enable/disable
        device.enable_dev()
        print("Device enabled!")
        time.sleep(10)
        device.disable_dev()
        print("Device disabled!")
        time.sleep(0.5)
        print("--------")



# Connect to SDR-14
try:
    device = sdr14()
except Exception as ex:
    print("No device connected!")
    sys.exit()

test_signal_out()


