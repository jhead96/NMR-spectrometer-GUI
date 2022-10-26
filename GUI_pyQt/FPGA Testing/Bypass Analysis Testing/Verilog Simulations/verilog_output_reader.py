import numpy as np
import matplotlib.pyplot as plt
import scipy.fft


def split_simulation_output(signal_in):

    # Get individual sample width
    l = len(signal_in[0]) // 4

    split_samples = []

    for row in signal_in:

        split_samples.append(row[3*l:])
        split_samples.append(row[2 * l:3 * l])
        split_samples.append(row[l:2 * l])
        split_samples.append(row[:l])

    split_samples = np.array(split_samples)

    return split_samples

def convert_signal_to_dec(signal_bin, N_bits):

    signal_dec = []
    for bin_string in signal_bin:
        signal_dec.append(twoscomp_bin_to_dec(bin_string, N_bits))

    signal_dec = np.array(signal_dec)

    return signal_dec

def twoscomp_bin_to_dec(bin_str, N_bits):

    sign_bit = int(bin_str[0])
    val = 0
    # Calculate decimal value of bits 12->0
    for pos, digit in enumerate(bin_str[1:]):
        power = (N_bits - 1) - (pos + 1)
        val += int(digit) * (2**power)

    # Include sign bit
    val -= sign_bit * (2 ** (N_bits-1))

    return val

def calculate_FFT(x, y, Ts):

    N = x.size

    yf = np.abs(scipy.fft.rfft(y))
    xf = scipy.fft.rfftfreq(N, Ts)

    return xf, yf

def save_data(t, y, xf, yf, filename, sim_params):

    # Make header
    param_str = "".join([k + "," + str(v) + "\n" for k,v in sim_params.items()])
    header_str = "[Parameters]\n" + param_str + "[DATA]\nt(s), signal, f(Hz), spectrum"

    np.array([t, y, xf, yf])
    # Save
    np.savetxt(filename, delimiter=",", header=header_str, comments="")



# Simulation parameters

set_num = 1  # Test set number
f_LO = 10  # LO frequency [MHz]
f_in = 1  # Input signal frequency [MHz]
bypass = 0  # Signal analysis bypass [0 = off, 1 = on]
comment = ""  # Comments

sim_params = {"Test set number": set_num,
              "LO frequency (MHz)": f_LO,
              "Input signal frequency (MHz)": f_in,
              "Bypass analysis enabled": bypass,
              "Comment": comment}

# Read simulation
simulation_filepath = r"test output data/test_set_2_output.txt"
simulation_data = np.loadtxt(simulation_filepath, dtype=str)

# Split data
split_data = split_simulation_output(simulation_data)

# Convert data
dec_data = convert_signal_to_dec(split_data, 16)

# Plot


# Generate t
N = dec_data.size
fs = 800e6
Ts = 1/fs



t = np.arange(0, N*Ts, Ts)

plt.plot(t, dec_data)

x, y = calculate_FFT(t, dec_data,Ts)
print((x[2]-x[1])/1e6)

plt.figure()
plt.plot(x, y)

save_data(t, dec_data, x, y, "test", sim_params)








"""
# Constants
N_bits = 14

# Read Verilog test data
filepath = r"test output data/analysis_disabled_100MHz_output.txt"
raw_data = np.loadtxt(filepath, dtype=str)

# Convert test data to decimal
bin_data = []
for s in raw_data:

    s4 = s[:14]
    s3 = s[16:30]
    s2 = s[32:46]
    s1 = s[48:62]

    bin_data.append(s1)
    bin_data.append(s2)
    bin_data.append(s3)
    bin_data.append(s4)

bin_data = np.array(bin_data)

# Read test signal input to Verilog
test_data_in = np.loadtxt(r"test input signals\test_signal_100MHz.txt", dtype=str)

# Convert test signal to decimal
test_data_dec = convert_signal_to_dec(test_data_in, N_bits)
plt.plot(test_data_dec)

# Convert simulation output to decimal
simulation_data_dec = convert_signal_to_dec(bin_data, N_bits)

plt.plot(simulation_data_dec)

# Set up t data
N = data.size
fs = 800e6
Ts = 1/fs

t = np.arange(0, N*Ts, Ts)

plt.plot(t/1e-6, data)
plt.xlabel("t (us)")

# Fourier transform
yf = np.abs(scipy.fft.fft(data)[:int(N/2)])
xf = scipy.fft.fftfreq(N, d=Ts)[:int(N/2)]

plt.figure()
plt.plot(xf/1e6, yf)
plt.xlabel("f (MHz)")"""
