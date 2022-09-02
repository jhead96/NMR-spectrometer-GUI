from scope_readers import GwInstekReader
import numpy as np


# FPGA version v0.5.2
# Data generated using 'single_pulse_testing' function within 'pulse_testing.py'
pulses = np.array([10, 20, 40, 100, 150, 200, 250, 500, 1000])
filenames = [f"pulse_test_data/three_pulse_test_data_v053/{i}us_single_pulse.CSV" for i in pulses]

for f in filenames:
    dataset = GwInstekReader(f)
    dataset.plot_data()

# Data generated using 'double_pulse_testing' function within 'pulse_testing.py'
filenames = np.array([f"pulse_test_data/three_pulse_test_data_v053/20_20_10_double_pulse.CSV",
                      f"pulse_test_data/three_pulse_test_data_v053/200_200_100_double_pulse.CSV"])

for f in filenames:
    dataset = GwInstekReader(f)
    dataset.plot_data()

# Data generated using 'three_pulse_testing' function within 'pulse_testing.py'
filenames = np.array([f"pulse_test_data/three_pulse_test_data_v053/20_10_20_10_20_three_pulse.CSV",
                      f"pulse_test_data/three_pulse_test_data_v053/200_100_200_200_200_three_pulse.CSV",
                      f"pulse_test_data/three_pulse_test_data_v053/2000_2000_1000_2000_2000_three_pulse.CSV"])

for f in filenames:
    dataset = GwInstekReader(f)
    dataset.plot_data()

