from scope_readers import GwInstekReader
import numpy as np

# FPGA version v0.5.1
# Data generated using 'single_pulse_testing' function within 'pulse_testing.py'

pulses = np.array([10, 20, 30, 40, 50, 100, 150, 200, 250, 500, 750, 1000])
filenames = [f"pulse_test_data/single_pulse_test_data_v051/{i}us_single_pulse.CSV" for i in pulses]

for f in filenames:
    dataset = GwInstekReader(f)
    dataset.plot_data()
