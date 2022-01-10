import numpy as np

# Peak to peak V
v_pp = 0.4
v_rms = v_pp / (2 * np.sqrt(2))
# Impedance
R = 50

# Power from FPGA in mW
p_fpga_mw = (v_rms ** 2) / R

# Power from FPGA in dBm
p_fpga_dbm = 10 * np.log10(p_fpga_mw/1e-3)

print(f'FPGA power output = {p_fpga_mw/1e-3} mW = {p_fpga_dbm} dBm')
