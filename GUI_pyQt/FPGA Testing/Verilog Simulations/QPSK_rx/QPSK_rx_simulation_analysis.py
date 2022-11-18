import verilog_simulation_analysis_functions
import numpy as np
import matplotlib.pyplot as plt


dir_path = r"simulation_outputs/10MHz/"
filenames = [f"{dir_path}testset4_I.txt", f"{dir_path}testset4_Q.txt"]
save_names = [f"{dir_path}10MHz_phase_270_I_decimal.txt", f"{dir_path}10MHz_phase_270_Q_decimal.txt"]

N_samples = 4
order_reversed = True
N_bits = 16
fs = 1600e6
f_test = 10e6

sim_params = [{'f': f_test, 'phase': 270}, {'f': f_test, 'phase': 270}]

# Save data to decimal
"""for i in range(0, 2):
    verilog_simulation_analysis_functions.main(sim_filepath=filenames[i],
                                               N_samples=N_samples,
                                               order_reversed=order_reversed,
                                               N_bits=N_bits,
                                               fs=fs,
                                               save_filename=save_names[i],
                                               sim_params=sim_params[i])"""

fig1, fig1_ax1 = plt.subplots()
data = np.zeros((2, 800, 2))
labs = ["I - ISIM", "Q - ISIM"]



# Read data and plot
for i in range(0, 2):
    data[:, :, i] = np.loadtxt(save_names[i], skiprows=5, delimiter=",")
    fig1_ax1.plot(data[0, :, i], data[1, :, i], label=labs[i])

t = data[0, ::8, 0]
w = 2*np.pi*f_test
phase = 7*np.pi/4

I_python = data.max() * np.sin(w*t + phase)
Q_python = data.max() * np.cos(w*t + phase)

fig1_ax1.set_prop_cycle(None)
fig1_ax1.plot(t, I_python, ".", label="I - sin($\omega t + 7\pi/4$)")
fig1_ax1.plot(t, Q_python, ".", label="Q - cos($\omega t + 7\pi/4$)")

fig1_ax1.set_xlabel("t (s)")
fig1_ax1.set_ylabel("signal")
fig1_ax1.set_title("10MHz test signal rx_QPSK.v output compared to Python output for $\phi_{rx}$ = '01'")
fig1_ax1.legend()

