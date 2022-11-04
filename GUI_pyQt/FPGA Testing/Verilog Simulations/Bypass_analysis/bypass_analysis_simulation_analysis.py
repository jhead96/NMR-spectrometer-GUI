import verilog_simulation_analysis_functions

# Input parameters
filepath = r"test output data/test_set_2_output.txt"
N_samples = 4
N_bits = 16
reverse = True
fs = 800e6

# Simulation parameters
set_num = 1  # Test set number
f_LO = 10  # LO frequency [MHz]
f_in = 1  # Input signal frequency [MHz]
bypass = 0  # Signal analysis bypass [0 = off, 1 = on]
comment = ""  # Comments

# Save file parameters
save_filename = "test.txt"

sim_params = {"Test set number": set_num,
              "LO frequency (MHz)": f_LO,
              "Input signal frequency (MHz)": f_in,
              "Bypass analysis enabled": bypass,
              "Comment": comment}


verilog_simulation_analysis_functions.main(filepath, N_samples, reverse, N_bits, fs, save_filename, sim_params)
