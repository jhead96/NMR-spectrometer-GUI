from scope_readers import TektronixReader
import numpy as np
import matplotlib.pyplot as plt

def generate_plots(x,y, title="", x_lims = None, y_lims = None):

    fig1, (ax1, ax2) = plt.subplots(1, 2)
    fig1.suptitle(title)

    ax1.plot(x, y)
    ax1.set_title("Full record")
    ax1.set_xlabel("t ($\mu$s)")
    ax1.set_ylabel("V (V)")

    ax2.plot(x, y)
    ax2.set_title("Start of P1 zoom in")
    ax2.set_xlabel("t ($\mu$s)")
    ax2.set_ylabel("V (V)")
    ax2.set_xlim(x_lims)
    ax2.set_ylim(y_lims)

# FPGA version v0.5.4
# Data generated using 'gated_RF_pulse_testing' function within 'pulse_testing.py'

data_10MHz = TektronixReader(f"FPGA_output_test_data/gated_RF_test_data/RF_10MHz_20_10_20_10_20us_pulses.CSV")

generate_plots(data_10MHz.t * 1e6, data_10MHz.y, "$f_{out}$ = 10 MHz, pulse sequence = 20-10-20-10-20$\mu$s", [17.75, 19.75], [-0.3, 0.3])

data_100MHz = TektronixReader(f"FPGA_output_test_data/gated_RF_test_data/RF_100MHz_20_10_20_10_20us_pulses.CSV")
generate_plots(data_100MHz.t * 1e6, data_100MHz.y, "$f_{out}$ = 100 MHz, pulse sequence = 20-10-20-10-20$\mu$s", [17.75, 18.25], [-0.3, 0.3])

data_200MHz = TektronixReader(f"FPGA_output_test_data/gated_RF_test_data/RF_200MHz_20_10_20_10_20us_pulses.csv")
generate_plots(data_200MHz.t * 1e6, data_200MHz.y, "$f_{out}$ = 200 MHz, pulse sequence = 20-10-20-10-20$\mu$s", [8.8, 9.2], [-0.3, 0.3])

data_213MHz = TektronixReader(f"FPGA_output_test_data/gated_RF_test_data/RF_213MHz_20_10_20_10_20us_pulses.csv")
generate_plots(data_213MHz.t * 1e6, data_213MHz.y, "$f_{out}$ = 213 MHz, pulse sequence = 20-10-20-10-20$\mu$s", [8.8, 9.2], [-0.3, 0.3])
