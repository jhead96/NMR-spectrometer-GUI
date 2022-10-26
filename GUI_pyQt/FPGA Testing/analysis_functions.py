import scipy.signal
import numpy as np


def calculate_RFFT(y: np.array, fs: float) -> tuple:

    # Calculate t axis
    N = y.size
    Ts = 1 / fs
    t = np.arange(0, N * Ts, Ts)

    # FFT
    yf = np.abs(scipy.fft.rfft(y))
    xf = scipy.fft.rfftfreq(N, d=Ts)

    return t, xf, yf



