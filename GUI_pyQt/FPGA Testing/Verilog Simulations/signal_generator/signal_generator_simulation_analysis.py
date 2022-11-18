import verilog_simulation_analysis_functions
import numpy as np
import matplotlib.pyplot as plt

dir_path = r"simulation_outputs/10_MHz/"
file_names = [f"{dir_path}testset1_{i}.txt" for i in ["LO_I", "LO_Q", "RF"]]

N_samples = [4, 4, 8]
order_reversed = True
N_bits = [16, 16, 14]
fs = 1600e6
f_test = 10e6
TX_phase = ["00", "01", "11", "10"]

sim_params = [{'f': f_test, TX_phase: "00", RX_phase: "00"}]


output_names = [f"{int(f_test/1e6)}MHz_{i}_output_decimal.txt" for i in ["LO_I", "LO_Q", "RF"]]