import numpy as np
import matplotlib.pyplot as plt
import scipy.signal, scipy.fft

class FID:

    def __init__(self, data_filepath: str, header_size: int, save_filepath: str):
        self.raw_data_filepath = data_filepath
        self.header_size = header_size
        self.save_filepath = save_filepath

        # Read data file
        self.raw_data = self.read_raw_data()
        self.header, self.expt_params = self.get_header()

        # Split data
        self.t = self.raw_data[:, 0]
        self.mx = self.raw_data[:, 1]
        self.my = self.raw_data[:, 2]

        # FFT raw data
        self.raw_xf, self.mx_fft = self.FFT_FID(self.t, self.mx)
        _, self.my_fft = self.FFT_FID(self.t, self.my)


        self.mag = self.calc_magnitude()

        self.N_data = len(self.t)
        

    def __str__(self) -> str:
        return f"{self.expt_params}"

    def read_raw_data(self) -> np.array:
        raw_data = np.loadtxt(self.raw_data_filepath, delimiter=" ", skiprows=self.header_size)
        return raw_data

    def get_header(self):
        header = []
        expt_params = []
        return header, expt_params

    
    def calc_magnitude(self) -> np.array:
        return ((self.mx ** 2) + (self.my ** 2)) ** 0.5 


    def save_processed_data(self, save_name, data) -> None:
        np.savetxt(save_name, data, header=self.header, comments="", delimter=",")


    def filter_FID(self, data, f_co:float, fs:float = 800e6) -> np.array:
        coeffs = self.generate_filter_coefficients(f_co, fs)
        filtered_data = scipy.signal.convolve(data, coeffs, mode="same")
        return filtered_data
        

    @staticmethod
    def trim_FID(data:np.array, start:int = 0, end:int = -1):
        return data[start:end]    
        
    @staticmethod
    def generate_filter_coefficients(f_cutoff: float, fs, n_taps : int = 51) -> np.array:
        coeffs = scipy.signal.firwin(n_taps, f_cutoff, fs=fs)
        return coeffs


    @staticmethod
    def FFT_FID(t: np.array, y: np.array) -> tuple[np.array, np.array]:
        ts = t[1] - t[0]
        N = len(t)
        yf = np.abs(scipy.fft.rfft(y))
        xf = scipy.fft.rfftfreq(N, ts)

        return xf, yf



    def plot_raw_FID(self) -> None:
        
        title = self.raw_data_filepath.split("\\")[-1]

        fig, ax = plt.subplots()

        ax.plot(self.t, self.mx, label="mx")
        ax.plot(self.t, self.my, label="my")
        ax.plot(self.t, self.mag, label="Magnitude")

        ax.set_title(f"Raw FID data for:\n{title}\n{self}")
        ax.set_xlabel("t (s)")
        ax.set_ylabel("signal")
        
        

x = FID(r"X:\chungm-quantum-magnetism\PhD projects\Jake Head\NMR Data\Cobalt Powder\spectrum_processed_data\213pt0_MHz_processed.txt", 10, "test")
x.plot_raw_FID()
mx_filt = x.filter_FID(x.mx, 200e6)
mx_filt_xf, mx_filt_fft = x.FFT_FID(x.t, mx_filt)

plt.figure()
plt.plot(x.raw_xf, x.mx_fft)
plt.plot(mx_filt_xf, mx_filt_fft)


plt.figure()
plt.plot(x.t, x.mx)
plt.plot(x.t, mx_filt)
plt.show()




