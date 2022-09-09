from scope_readers import TektronixReader
import numpy as np


# FPGA version v0.5.4
# Data generated using 'gated_RF_pulse_testing' function within 'pulse_testing.py'

filename = f"FPGA_output_test_data/gated_RF_test_data/RF_10MHz_20_10_20_10_20us_pulses.CSV"

data = TektronixReader(filename)

data.plot_data()