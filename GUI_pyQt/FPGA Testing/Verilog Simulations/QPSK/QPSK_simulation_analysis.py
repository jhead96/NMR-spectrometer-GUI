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

output_names = [f"{int(f_test/1e6)}MHz_phase{p}_{N_bits}bitoutput_decimal.txt" for p in phases]

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


fig1_ax1.set_title(f"{int(f_test/1e6)} MHz simulation 14-bit outputs (-) compared to Python generated phase shifted waves (.)")
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


"""# IQ swapped simulations
IQ_swapped_filenames = [f"{dir_path}IQswapped_testset{i}_14bitoutput.txt" for i in range(1, 5)]
IQ_swapped_output_names = [f"IQswapped_{int(f_test/1e6)}MHz_phase{p}_output_decimal.txt" for p in phases]


for i in range(0, 4):
    verilog_simulation_analysis_functions.main(sim_filepath=IQ_swapped_filenames[i],
                                               N_samples=N_samples,
                                               order_reversed=order_reversed,
                                               N_bits=N_bits,
                                               fs=fs,
                                               save_filename=IQ_swapped_output_names[i],
                                               sim_params=sim_params[i])


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
"""


# 16-bit outputs
N_bits = 16
filenames_16bits = [f"{dir_path}testset{i}_{N_bits}bitoutput.txt" for i in range(1, 5)]
save_filenames_16bits_names = [f"{int(f_test/1e6)}MHz_phase{p}_{N_bits}bitoutput_decimal.txt" for p in phases]


"""for i in range(0, 4):
    verilog_simulation_analysis_functions.main(sim_filepath=filenames_16bits[i],
                                               N_samples=N_samples,
                                               order_reversed=order_reversed,
                                               N_bits=N_bits,
                                               fs=fs,
                                               save_filename=save_filenames_16bits_names[i],
                                               sim_params=sim_params[i])"""

data_16bit = np.zeros((2, 800, 4))
fig3, fig3_ax1 = plt.subplots()
# Read data and plot
for i in range(0, 4):
    data_16bit[:, :, i] = np.loadtxt(dir_path + save_filenames_16bits_names[i], skiprows=5, delimiter=",")
    fig3_ax1.plot(data_16bit[0, :, i], data_16bit[1, :, i], label=f"rf_ph='{rf_ph[i]}'")

fig3_ax1.set_prop_cycle(None)

test_phases = [5*np.pi/4, 3*np.pi/4, np.pi/4, 7*np.pi/4]
test_phases_labels= ["$5\pi$/4", "3$\pi$/4", "$\pi$/4", "$7\pi$/4"]

for i, ph in enumerate(test_phases):
    test_wave = data_16bit.max() * np.sin(omega*t + ph)
    fig3_ax1.plot(t, test_wave, '.', markersize=5, label=f"sin($\omega t$ + {test_phases_labels[i]})")

fig3_ax1.set_title(f"16-bit {int(f_test/1e6)} MHz simulation outputs (-) compared to Python generated phase shifted waves (.)")
fig3_ax1.set_xlabel("t (s)")
fig3_ax1.set_ylabel("signal")
fig3_ax1.legend()

# 16-bit, 4 parallel outputs
N_samples = 4
N_bits = 16
filenames_16bits_4para = [f"{dir_path}testset{i}_{N_bits}bitoutput_4parallel.txt" for i in range(1, 5)]
save_filenames_16bits_4para_names = [f"{int(f_test/1e6)}MHz_phase{p}_{N_bits}bitoutput_4parallel_decimal.txt" for p in phases]


"""for i in range(0, 4):
    verilog_simulation_analysis_functions.main(sim_filepath=filenames_16bits_4para[i],
                                               N_samples=N_samples,
                                               order_reversed=order_reversed,
                                               N_bits=N_bits,
                                               fs=fs,
                                               save_filename=save_filenames_16bits_4para_names[i],
                                               sim_params=sim_params[i])"""

data_16bit_4para = np.zeros((2, 800, 4))
fig4, fig4_ax1 = plt.subplots()
# Read data and plot
for i in range(0, 4):
    data_16bit_4para[:, :, i] = np.loadtxt(dir_path + save_filenames_16bits_4para_names[i], skiprows=5, delimiter=",")
    fig4_ax1.plot(data_16bit_4para[0, :, i], data_16bit_4para[1, :, i], label=f"rf_ph='{rf_ph[i]}'")

fig4_ax1.set_prop_cycle(None)

test_phases = [5*np.pi/4, 3*np.pi/4, np.pi/4, 7*np.pi/4]
test_phases_labels= ["$5\pi$/4", "3$\pi$/4", "$\pi$/4", "$7\pi$/4"]

for i, ph in enumerate(test_phases):
    test_wave = data_16bit.max() * np.sin(omega*t + ph)
    fig4_ax1.plot(t, test_wave, '.', markersize=5, label=f"sin($\omega t$ + {test_phases_labels[i]})")

fig4_ax1.set_title(f"4 parallel, 16-bit {int(f_test/1e6)} MHz simulation outputs (-) compared to Python generated phase shifted waves (.)")
fig4_ax1.set_xlabel("t (s)")
fig4_ax1.set_ylabel("signal")
fig4_ax1.legend()