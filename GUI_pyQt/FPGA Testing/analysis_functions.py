import scipy.signal
import numpy as np
import os

def calculate_RFFT(y: np.array, fs: float) -> tuple:

    # Calculate t axis
    N = y.size
    Ts = 1 / fs
    t = np.arange(0, N * Ts, Ts)

    # FFT
    yf = np.abs(scipy.fft.rfft(y))
    xf = scipy.fft.rfftfreq(N, d=Ts)

    return t, xf, yf

def generate_datafile_header(**kwargs) -> str:
    return "[Parameters]\n" + "".join([f"{k}, {v}\n" for k, v in kwargs.items()]) + "t (us), Ch1, Ch2\n[Data]"

def save_analyzed_data(data: tuple, filepath: str, header: str):

    print(os.path.exists(filepath))
    if os.path.exists(filepath):
        print("File already exists!")
    else:
        np.savetxt(filepath, data, header=header, comments="")
        print(f"File saved to {filepath}")



