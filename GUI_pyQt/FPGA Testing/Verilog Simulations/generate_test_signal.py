import test_signal_generation_functions

# Inputs
f = 10e6
fs = 1600e6
N_lines = 800
N_bits = 16
sig_type = "cos"


test_signal_generation_functions.main(f, fs, N_lines, N_bits, sig_type)
