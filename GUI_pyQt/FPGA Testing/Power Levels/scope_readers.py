import matplotlib.pyplot as plt
import numpy as np
import scipy.fft

class TektronixReader():

    def __init__(self, filepath):

        self.filepath = filepath
        self.y, self.N, self.delta_t, self.fs = self.read_data()
        self.t = self.generate_t()
        self.xf, self.yf, self.intensity = self.calc_FFT()
        self.amp = self.calc_amp()
        self.PSD, self.power = self.calc_power()

    def read_data(self):
        data = np.genfromtxt(self.filepath, delimiter=",")

        y = data[:, 4]
        N = int(data[0, 1])
        delta_t = data[1, 1]

        return y, N, delta_t, 1/delta_t

    def generate_t(self):

        t = np.arange(0, self.N*self.delta_t, self.delta_t)

        return t

    def calc_amp(self):

        amp = np.max(self.y) - np.min(self.y)

        return np.round(amp,2)

    def calc_FFT(self):

        yf = scipy.fft.fft(self.y)[:int(self.N/2)]
        xf = scipy.fft.fftfreq(self.N, self.delta_t)[:int(self.N/2)]
        # Zero the DC component
        yf[0] = 0

        return xf, yf, np.abs(yf)

    def calc_power(self):

        # Impedance
        R = 50

        PSD = self.intensity / (2*self.fs)
        power = np.trapz(PSD, self.xf) / R

        return PSD, power

    def plot_data(self):

        fig, ax1 = plt.subplots()

        ax1.plot(self.t*1e6, self.y)
        ax1.set_title(self.filepath.split("/")[-1])
        ax1.set_xlabel("t ($\mu$s)")
        ax1.set_ylabel("V (V)")

    def plot_intensity(self):

        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.suptitle(f"{self.filepath}")
        ax1.plot(self.t, self.y)
        ax1.set_title(f"$V(t)$, $V_{{pp}} \\approx$ {self.amp}V")
        ax1.set_xlabel("t (s)")
        ax1.set_ylabel("V (V)")

        ax2.plot(self.xf, self.intensity)

        ax2.set_title("FFT")
        ax2.set_xlabel("f (Hz)")
        ax2.set_ylabel("Intensity ($V^2$)")
        # If FFT range includes Fs, plot Fs
        if np.max(self.xf) > 1.6e9:
            ax2.vlines(1.6e9, 0, np.max(self.intensity) / 2, linestyles="dashed", label="FPGA sampling frequency")
            ax2.set_xlim(0, 2.5e9)
            ax2.legend(loc="upper center")

    def plot_PSD(self):

        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.suptitle(f"{self.filepath}")
        ax1.plot(self.t, self.y)
        ax1.set_title(f"$V(t)$, $V_{{pp}} \\approx$ {self.amp}V")
        ax1.set_xlabel("t (s)")
        ax1.set_ylabel("V (V)")

        ax2.plot(self.xf, self.PSD)

        ax2.set_title("PSD (calculated from FFT)")
        ax2.set_xlabel("f (Hz)")
        ax2.set_ylabel("$P(f)$ ($V^2/Hz$)")
        # If FFT range includes Fs, plot Fs
        if np.max(self.xf) > 1.6e9:
            ax2.vlines(1.6e9, 0, np.max(self.PSD) / 2, linestyles="dashed", label="FPGA sampling frequency")
            ax2.set_xlim(0, 2.5e9)
            ax2.legend(loc="upper center")

class GwInstekReader():

    def __init__(self, filepath: str):

        self.filepath = filepath
        # Read data
        self.data = self.read_data()

        # Extract useful params
        self.N = self.data[0, 1]
        self.Ts = self.data[11, 1]
        # V/div -> V/pt
        self.y_scale = self.data[5, 1] / 25

        # Scale y
        self.y = self.data[16:, 0] * self.y_scale
        # Generate t
        self.t = np.arange(0, self.N) * self.Ts


    def read_data(self):

        data = np.genfromtxt(self.filepath, delimiter=",", usecols=(0, 1))

        return data

    def plot_data(self):

        fig1, ax1 = plt.subplots()

        ax1.plot(self.t * 1e6, self.y)
        ax1.set_title(self.filepath.split("/")[-1])
        ax1.set_xlabel("t ($\mu$s)")
        ax1.set_ylabel("V (V)")

