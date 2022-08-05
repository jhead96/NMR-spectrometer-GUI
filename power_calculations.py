import numpy as np


def W_to_dBm(P_in):
    return 10 * np.log10(P_in*1e3)

def dBm_to_mW(P_in):
    return 10 ** (P_in/10)

def calc_power(V_pp):
    # Impedance
    R = 50

    # FPGA output
    V_rms = V_pp / (2 * np.sqrt(2))
    P_FPGA_W = (V_rms ** 2) / R
    P_FPGA_dBm = W_to_dBm(P_FPGA_W)
    print(f'FPGA power output = {P_FPGA_W / 1e-3} mW, = {P_FPGA_dBm} dBm')

    # Amplifier output
    amp_gain = 60
    P_amp_dBm = P_FPGA_dBm + amp_gain
    P_amp_mW = dBm_to_mW(P_amp_dBm)
    print(f'Amplifier main power output = {P_amp_mW / 1e3:.2f} W, = {P_amp_dBm} dBm')

    # Sample output
    sample_gain = -50
    P_sample_dBm = P_amp_dBm + sample_gain
    P_sample_mW = dBm_to_mW(P_sample_dBm)
    print(f'Sample channel power output = {P_sample_mW} mW, = {P_sample_dBm} dBm')

    # Oscilloscope max input
    V_rms_max = 5
    P_scope_max_W = (V_rms_max ** 2) / R
    P_scope_max_dBm = W_to_dBm(P_scope_max_W)
    print(f'Oscilloscope max power input = {P_scope_max_W} W, = {P_scope_max_dBm} dBm')





V = 0.4
calc_power(V)


