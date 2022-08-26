from scope_readers import GwInstekReader
import numpy as np

pulses = np.array([10, 20, 30, 40, 50, 100, 150, 200, 250, 500, 750, 1000])

filenames = [f"single_pulse_testing_data/{i}us_single_pulse.CSV" for i in pulses]

for f in filenames:
    dataset = GwInstekReader(f)
    dataset.plot_data()
