from ADQ_tools_lite import sdr14
import analysis_functions
import matplotlib.pyplot as plt
import numpy as np
import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sys

class LiveDataCollection(QObject):

    # Signals
    finished = pyqtSignal()
    data_out = pyqtSignal(int, object, object, object, object)

    def __init__(self, dev, N_scans, params, N=65536):
        super().__init__()
        self.dev = dev
        self.N = N
        self.N_scans = N_scans
        self.params = params
        if dev:
            self.init_expt()
            self.init_acq()

    def init_expt(self):
        # Define regs
        f_reg = 1
        P1_reg = 2
        P2_reg = 3
        G1_reg = 5
        rec_reg = 7

        # Set up two pulse sequence
        f = int(self.params["f"])
        P1 = int(self.params["P1"])
        P2 = int(self.params["P2"])
        G1 = int(self.params["G1"])
        rec = int(self.params["rec"])

        # Write values
        self.dev.reg_write(f_reg, f)
        self.dev.reg_write(P1_reg, P1)
        self.dev.reg_write(P2_reg, P2)
        self.dev.reg_write(G1_reg, G1)
        self.dev.reg_write(rec_reg, rec)
        print("Experiment set-up complete")

    def init_acq(self):
        # Set up acquisition
        self.dev.set_clock_source()
        self.dev.set_MR_settings()
        self.dev.set_trigger_mode("EXTERNAL")
        self.dev.set_external_trig_edge()

    def run_expt(self):
        ch1_total = np.zeros(N)
        ch2_total = np.zeros(N)

        for i in range(N_scans):
            # Get data
            ch1, ch2 = self.dev.External_MR_acquisition("0")
            # Increment total
            ch1_total += ch1
            ch2_total += ch2
            print(ch1[0])
            print(ch1_total[0])
            self.data_out.emit(i, ch1, ch2, ch1_total/(i+1), ch2_total/(i+1))
            time.sleep(0.1)

    def run_demo(self):
        ch1_total = np.zeros(N)
        ch2_total = np.zeros(N)

        for i in range(N_scans):
            # Get data
            ch1 = (np.random.random(N) - 0.5) * 100
            ch2 = (np.random.random(N) - 0.5) * 100
            # Increment total
            ch1_total += ch1
            ch2_total += ch2
            self.data_out.emit(i, ch1, ch2, ch1_total / (i + 1), ch2_total / (i + 1))
            time.sleep(2)

    def choose_mode(self):

        self.run_expt() if self.dev else self.run_demo()


def plot_data_from_worker(scan, ch1, ch2, ch1_avg, ch2_avg):
    # ax1
    avgline1.set_data(t/1e-6, ch1_avg)
    avgline2.set_data(t/1e-6, ch2_avg)
    ax1.set_title(f"Average spectrometer signal for scan {scan}/{N_scans-1}")

    # ax2
    line1.set_data(t/1e-6, ch1)
    line2.set_data(t/1e-6, ch2)
    ax2.set_title(f"Spectrometer signal for scan {scan}/{N_scans-1}")
    plt.draw()

    """# Calculate avg magnitude
    magnitude = np.sqrt((ch1_avg ** 2) + (ch2_avg ** 2))

    # Plot magnitude
    magline.set_data(t/1e-6, magnitude)
    fig2_ax1.set_title(f"Magnitude of spectrometer signal for scan {scan}/{N_scans-1}")
    plt.draw()"""

    # Save ch1, ch2 to file
    header = analysis_functions.generate_datafile_header(**params)
    np.savetxt(f"{save_filename}_{scan}.txt", (t/1e-6, ch1, ch2), header=header, comments="")

def init_plots():
    # Initialize figures
    fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # ax1
    avgline1, = ax1.plot([], [], "b-", label="Ch1")
    avgline2, = ax1.plot([], [], "r-", label="Ch2")
    ax1.set_xlabel("t (us)")
    ax1.set_ylabel("Signal")
    ax1.set_xlim(0, 85)
    ax1.set_ylim(-100, 100)
    ax1.legend()

    # ax2
    line1, = ax2.plot([], [], "b-", label="Ch1")
    line2, = ax2.plot([], [], "r-", label="Ch2")
    ax2.set_xlabel("t (us)")
    ax2.set_ylabel("Signal")
    ax2.set_xlim(0, 85)
    ax2.set_ylim(-100, 100)
    ax2.legend()

    """fig2, fig2_ax1 = plt.subplots()
    magline, = fig2_ax1.plot([], [], "g-")
    fig2_ax1.set_xlabel("t (us)")
    fig2_ax1.set_ylabel("Signal")
    fig2_ax1.set_xlim(0, 85)
    fig2_ax1.set_ylim(-100, 100)"""

    return fig1, ax1, line1, line2, ax2, avgline1, avgline2

def find_sdr14():
    # Connect to SDR-14
    try:
        device = sdr14()
    except Exception as ex:
        device = None
        print("No device connected!")
        # sys.exit()
    return device

# Get sdr14
device = find_sdr14()

# Initialise plots
fig1, ax1, line1, line2, ax2, avgline1, avgline2 = init_plots()


# Experimental parameters
params = {"f": 213e6, "P1": 2e3, "P2": 4e3, "G1": 10e3, "rec": 10e3, "atten": 10}

# Number of scans
N_scans = 30

N = 65536
fs = 800e6
Ts = 1/fs
t = np.arange(0, N*Ts, Ts)

# Save parameters
save_filename = "test_data"

# Make SDR14 worker thread
# Setup new thread for continuous acquisition
liveThread = QThread()
liveWorker = LiveDataCollection(device, N_scans, params)
liveWorker.moveToThread(liveThread)

liveThread.started.connect(liveWorker.choose_mode)
liveThread.finished.connect(liveThread.deleteLater)

liveWorker.data_out.connect(plot_data_from_worker)
liveWorker.finished.connect(liveThread.quit)
liveWorker.finished.connect(liveWorker.deleteLater)

# Start thread
liveThread.start()
