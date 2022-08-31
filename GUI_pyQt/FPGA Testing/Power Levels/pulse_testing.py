from ADQ_tools_lite import sdr14
import numpy as np
import time
import sys

def single_pulse_testing():
    """
    Function for generating a set single square pulse test dataset.
    """

    # Define pulse widths [ns]
    P1 = np.array([10, 20, 30, 40, 50, 100, 150, 200, 250, 500, 750, 1000]) * 1000
    # Define regs
    P1_reg = 2
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
        time.sleep(10)
        device.disable_dev()
        print("Device disabled!")
        time.sleep(0.5)
        print("--------")

    print("Single pulse tests complete!")
    input("Press any key to continue...")

def double_pulse_testing():
    """
    Function for generating a set of double pulse sequence test dataset.
    """

    P1_reg = 2
    P2_reg = 3
    G1_reg = 4

    # Test two pulses
    P1 = np.array([20, 200, 2000]) * 1000
    P2 = np.array([10, 100, 1000]) * 1000
    G1 = np.array([20, 200, 2000]) * 1000

    for p1, p2, g1 in zip(P1, P2, G1):

        # Write
        if not device.reg_write(P1_reg, p1):
            print("Write unsuccessful, exiting ...")
            break
        if not device.reg_write(P2_reg, p2):
            print("Write unsuccessful, exiting ...")
            break
        if not device.reg_write(G1_reg, g1):
            print("Write unsuccessful, exiting ...")
            break

        time.sleep(0.5)
        # Enable/disable
        device.enable_dev()
        print("Device enabled!")
        time.sleep(15)
        device.disable_dev()
        print("Device disabled!")
        time.sleep(0.5)
        print("--------")

    input("Double pulse testing completed! Press any key to continue ...")

def three_pulse_testing():
    """
    Function for generating a three pulse sequence test dataset.
    :return:
    """
    pass

def repeat_testing():
    """
    Function for testing if the pulse sequence is repeating itself correctly.
    """

    # Write pulses
    device.reg_write(2, 20000)
    device.reg_write(3, 10000)
    device.reg_write(4, 20000)


    for i in range(5):
        device.enable_dev()
        time.sleep(10)
        device.disable_dev()
        time.sleep(5)
    print("Finished!")


# Connect to SDR-14
try:
    device = sdr14()
except Exception as ex:
    print("No device connected!")
    sys.exit()


#single_pulse_testing()
#double_pulse_testing()
repeat_testing()







