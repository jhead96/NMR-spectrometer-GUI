import numpy as np
import matplotlib.pyplot as plt


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

    def calc_magnitude(self):
        pass

    def FFT_FID(self):
        pass

    def plot_FID(self):
        pass