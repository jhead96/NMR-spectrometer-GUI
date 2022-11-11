import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import scipy.fft


def split_simulation_output(signal_in: np.ndarray[str], N_samples: int, samples_reversed: bool)-> np.ndarray[str]:

    # Get individual sample width
    l = len(signal_in[0]) // N_samples

    # Calculate individual sample start/end indexes
    start_indexes = [i * l for i in range(0, N_samples)]
    end_indexes = [(i * l) - 1 for i in range(1, N_samples+1)]

    # Handle reversed sample order
    if samples_reversed:
        start_indexes = list(reversed(start_indexes))
        end_indexes = list(reversed(end_indexes))

    split_samples = []
    # Iterate rows
    for row in signal_in:
        # Iterate samples in row
        for s, e in zip(start_indexes, end_indexes):
            # Separate samples
            split_samples.append(row[s:e])

    return np.array(split_samples)


def convert_signal_to_dec(signal_bin: np.ndarray[str], N_bits: int) -> np.ndarray[float]:

    signal_dec = []
    for bin_string in signal_bin:
        signal_dec.append(twoscomp_bin_to_dec(bin_string, N_bits))

    signal_dec = np.array(signal_dec)

    return signal_dec


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


def calculate_FFT(x: np.ndarray[float], y: np.ndarray[float], Ts: float) -> tuple[np.ndarray[float], np.ndarray[float]]:

    N = x.size

    yf = np.abs(scipy.fft.rfft(y))
    xf = scipy.fft.rfftfreq(N, Ts)

    return xf, yf


def plot_data(x: np.ndarray[float], y: np.ndarray[float]) -> tuple[plt.figure, plt.axes]:
    fig, ax = plt.subplots()
    ax.plot(x, y)

    return fig, ax


def save_data(t: np.ndarray[float], y: np.ndarray[float], filename: str, **kwargs):

    # Make header
    param_str = "".join([k + "," + str(v) + "\n" for k, v in kwargs.items()])
    header_str = "[Parameters]\n" + param_str + "[DATA]\nt(s), signal"

    np.array([t, y])
    # Save
    np.savetxt(filename, (t, y), delimiter=",", header=header_str, comments="")


def main(sim_filepath: str, N_samples: int, order_reversed: bool, N_bits: int, fs: float,
         save_filename: str, sim_params: dict):
    """
    Read data from a Verilog simulation output given the number of samples per line and the bit width of the samples.
    Time series and FFT data is plotted automatically

    :param sim_filepath: Filepath to Verilog simulation file
    :param N_samples: Number of samples per line.
    :param order_reversed: True if time ordering of samples goes from right -> left
    :param N_bits: Number of bits to use when converting to signed decimal.
    :param fs: Sampling frequency used in FFT.
    :param save_filename: Name of saved decimal file
    :param sim_params: Dictionary of parameters to used in the header in saved decimal datafile
    :return:
    """

    # Read simulation data
    simulation_data = np.loadtxt(sim_filepath, dtype=str)
    # Split data
    split_data = split_simulation_output(simulation_data, N_samples, order_reversed)
    # Convert to dec
    dec_data = convert_signal_to_dec(split_data, N_bits)

    # Generate t
    N = dec_data.size
    Ts = 1 / fs
    t = np.arange(0, N * Ts, Ts)

    # Calculate FFT
    f, yf = calculate_FFT(t, dec_data, Ts)

    # Plot
    plot_data(t, dec_data)
    plot_data(f, yf)

    # Save processed data to file
    save_data(t, dec_data, save_filename, **sim_params)