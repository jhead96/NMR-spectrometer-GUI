import verilog_simulation_analysis_functions
import numpy as np
import matplotlib.pyplot as plt

dir_path = r"simulation_outputs/10_MHz/"
file_names = [f"{dir_path}testset{i}_14bitoutput.txt" for i in range(1, 5)]

N_samples = 8
order_reversed = True
N_bits = 14
fs = 1600e6
f_test = 10e6
phases = [0, 90, 180, 270]
rf_ph = ["00", "01", "11", "10"]
shift = [0, 3*np.pi/2, np.pi, np.pi/2]

sim_params = [{'f': f_test, 'phase': p} for p in phases]

output_names = [f"{int(f_test/1e6)}MHz_phase{p}_output_decimal.txt" for p in phases]

"""# Save data to decimal
for i in range(0, 4):
    verilog_simulation_analysis_functions.main(sim_filepath=file_names[i],
                                               N_samples=N_samples,
                                               order_reversed=order_reversed,
                                               N_bits=N_bits,
                                               fs=fs,
                                               save_filename=output_names[i],
                                               sim_params=sim_params[i])"""

fig1, fig1_ax1 = plt.subplots()


data = np.zeros((2, 800, 4))
# Read data and plot
for i in range(0, 4):
    data[:, :, i] = np.loadtxt(dir_path + output_names[i], skiprows=5, delimiter=",")
    fig1_ax1.plot(data[0, :, i], data[1, :, i], label=f"rf_ph='{rf_ph[i]}'")


fig1_ax1.set_title(f"{int(f_test/1e6)} MHz simulation outputs (-) compared to Python generated phase shifted waves (.)")
fig1_ax1.set_xlabel("t (s)")
fig1_ax1.set_ylabel("signal")


# Generate comparison waves

test_phases = [5*np.pi/4, 7*np.pi/4, np.pi/4, 3*np.pi/4]
test_phases_labels= ["$5\pi$/4", "7$\pi$/4", "$\pi$/4", "$3\pi$/4"]
t = data[0, ::16, 0]
omega = 2*np.pi*f_test

fig1_ax1.set_prop_cycle(None)

for i, ph in enumerate(test_phases):
    test_wave = data.max() * np.sin(omega*t + ph)
    fig1_ax1.plot(t, test_wave, '.', markersize=5, label=f"sin($\omega t$ + {test_phases_labels[i]})")

fig1_ax1.legend()


# IQ swapped simulations
IQ_swapped_filenames = [f"{dir_path}IQswapped_testset{i}_14bitoutput.txt" for i in range(1, 5)]
IQ_swapped_output_names = [f"IQswapped_{int(f_test/1e6)}MHz_phase{p}_output_decimal.txt" for p in phases]


"""for i in range(0, 4):
    verilog_simulation_analysis_functions.main(sim_filepath=IQ_swapped_filenames[i],
                                               N_samples=N_samples,
                                               order_reversed=order_reversed,
                                               N_bits=N_bits,
                                               fs=fs,
                                               save_filename=IQ_swapped_output_names[i],
                                               sim_params=sim_params[i])"""


IQ_swapped_data = np.zeros((2, 800, 4))
fig2, fig2_ax1 = plt.subplots()

# Read data and plot
for i in range(0, 4):
    IQ_swapped_data[:, :, i] = np.loadtxt(dir_path + IQ_swapped_output_names[i], skiprows=5, delimiter=",")
    fig2_ax1.plot(IQ_swapped_data[0, :, i], IQ_swapped_data[1, :, i], label=f"rf_ph='{rf_ph[i]}'")


fig2_ax1.set_title(f"IQ swapped {int(f_test/1e6)} MHz simulation outputs (-)")
fig2_ax1.set_xlabel("t (s)")
fig2_ax1.set_ylabel("signal")
fig2_ax1.legend()