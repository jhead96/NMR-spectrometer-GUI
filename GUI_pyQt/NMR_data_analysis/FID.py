import numpy as np
import matplotlib.pyplot as plt
import scipy.signal

class FID:

    def __init__(self, data_filepath, save_filepath):
        self.raw_data_filepath = data_filepath
        self.save_filepath = save_filepath

        self.raw_FID = self.read_raw_data()
        self.header, self.expt_params = self.get_header()

    def __str__(self):
        return f"{self.expt_params}"

    def read_raw_data(self):
        raw_data = np.loadtxt(self.raw_data_filepath, delimiter=",")
        return raw_data

    def get_header(self):
        header = []
        expt_params = []
        return header, expt_params

    def save_processed_data(self, save_name, data):
        np.savetxt(save_name, data, header=self.header, comments="", delimter=",")

    def trim_FID(self, FID_length):
        pass

    def filter_FID(self, f_co):
        pass

    @staticmethod
    def generate_filter_coefficients(f_cutoff: float, fs, n_taps : int) -> np.array:
        coeffs = scipy.signal.firwin(n_taps, f_cutoff, fs=fs)
        return coeffs

    def calc_magnitude(self):
        pass

    def FFT_FID(self):
        pass

    def plot_FID(self):
        pass


t = FID.generate_filter_coefficients(100e6, 400e6, 23)

w, h = scipy.signal.freqz(t, fs=400e6)
plt.plot(w, 10*np.log10(np.abs(h)))
