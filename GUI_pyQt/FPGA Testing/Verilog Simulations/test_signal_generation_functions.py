import numpy as np
import scipy.fft
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt


def generate_test_signal(f: float, fs: float, N: int, N_bits: int, sig_type: str = "sin") -> tuple[np.ndarray, any, np.ndarray[str]]:

    # Signal parameters
    Ts = 1 / fs
    T = Ts * N
    t = np.arange(0, T, Ts)
    omega_0 = 2 * np.pi * f

    # Generate signal
    if sig_type == "sin":
        test_signal = np.sin(omega_0 * t)
    elif sig_type == "cos":
        test_signal = np.cos(omega_0 * t)
    else:
        test_signal = None
        print("Invalid test signal type")

    # Scale to fit in N_bits
    scale_factor = (2**(N_bits-1) - 1)

    scaled_test_signal = np.round(test_signal * scale_factor).astype(int)

    scaled_test_signal_fp = f"input_signals/{N_bits}bit_{sig_type}_test_signal_{int(f / 1e6)}MHz.txt"

    saved_binary_data = generate_binary_file(scaled_test_signal, N_bits, scaled_test_signal_fp)

    return t, scaled_test_signal, saved_binary_data


def generate_binary_file(data: np.ndarray[str], b: int, filename: str) -> np.ndarray[str]:
    """
    Generate binary files.
    :param data: Data to be written to file.
    :param b: Amount of bits.
    :param filename: Name of file to be written to.
    """

    binary_data = []
    with open(filename, 'a') as filename:
        for i in range(len(data)):
            data_bin = '{0:{fill}{width}b}'.format((data[i] + 2 ** b) % 2 ** b, fill='0', width=b)
            filename.write(data_bin + '\n')
            binary_data.append(data_bin)

    return np.array(binary_data)


def generate_FFT(t: np.ndarray[float], signal: np.ndarray[float]) -> tuple[np.ndarray[float], np.ndarray[float]]:

    N = signal.size
    Ts = t[1] - t[0]

    yf = np.abs(scipy.fft.rfft(signal))
    xf = scipy.fft.rfftfreq(N, d=Ts)

    return xf, yf


def plot_signal(f: float, t: np.ndarray[float], signal: np.ndarray[float], xf: np.ndarray[float], yf: np.ndarray[float]):

    fig1, (ax1, ax2) = plt.subplots(1, 2)

    ax1.plot(t/1e-6, signal)
    ax1.set_xlabel("t (us)")
    ax1.set_ylabel("Signal")
    ax1.set_title(f"{int(f/1e6)}MHz test signal")

    ax2.plot(xf / 1e6, yf)
    ax2.set_xlabel("f (MHz)")
    ax2.set_ylabel("Intensity")
    ax2.set_title(f"FFT of {int(f / 1e6)}MHz test signal")


def read_test_signal(f: float, N_bits: int, sig_type: str) -> np.ndarray[int]:


    filename = f"input_signals/{N_bits}bit_{sig_type}_test_signal_{int(f / 1e6)}MHz.txt"
    data_from_file = np.loadtxt(filename, dtype=str)

    file_data_decimal = []

    for d in data_from_file:
        file_data_decimal.append(twoscomp_bin_to_dec(d, 14))

    return np.array(file_data_decimal)


def twoscomp_bin_to_dec(bin_str: str, N_bits: int) -> int:

    sign_bit = int(bin_str[0])
    val = 0
    # Calculate decimal value of bits 12->0
    for pos, digit in enumerate(bin_str[1:]):
        power = (N_bits - 1) - (pos + 1)
        val += int(digit) * (2**power)

    # Include sign bit
    val -= sign_bit * (2 ** (N_bits-1))

    return val


def main(f: float, fs: float, N_lines: int, N_bits: int, sig_type: str):

    # Generate the signals
    t, sig, saved_binary_data = generate_test_signal(f, fs, N_lines, N_bits, sig_type)
    xf, yf = generate_FFT(t, sig)

    # Plot
    plot_signal(f, t, sig, xf, yf)

    # Read back to confirm binary data matches
    sig_from_file = read_test_signal(f, N_bits, sig_type)

    if np.all(sig_from_file == read_test_signal(f, N_bits, sig_type)):
        print("Data read from file matches generated data!")
    else:
        print("Error in file write")


