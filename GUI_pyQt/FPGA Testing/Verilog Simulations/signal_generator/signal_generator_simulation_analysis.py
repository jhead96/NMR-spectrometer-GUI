import verilog_simulation_analysis_functions
import numpy as np
import matplotlib.pyplot as plt

dir_path = r"simulation_outputs/10MHz/"
file_names = [f"{dir_path}testset1_{i}.txt" for i in ["LO_I", "LO_Q", "RF"]]

N_samples = [4, 4, 8]
order_reversed = True
N_bits = [16, 16, 14]
fs = [800e6, 800e6, 1600e6]
f_test = 10e6
TX_phase = ["00", "01", "11", "10"]

sim_params = {'f': f_test, 'TX_phase': "00", 'RX_phase': "00"}

output_names = [f"{int(f_test/1e6)}MHz_{i}_output_decimal.txt" for i in ["LO_I", "LO_Q", "RF"]]


"""# Save data to decimal
for i in range(0, 3):
    verilog_simulation_analysis_functions.main(sim_filepath=file_names[i],
                                               N_samples=N_samples[i],
                                               order_reversed=order_reversed,
                                               N_bits=N_bits[i],
                                               fs=fs[i],
                                               save_filename=output_names[i],
                                               sim_params=sim_params)"""

fig1, fig1_ax1 = plt.subplots()
data_length = 248
IQ_data = np.zeros((2, data_length, 2))
labs = ["I - ISIM", "Q - ISIM"]


# Read IQ data and plot
for i in range(0, 2):
    IQ_data[:, :, i] = np.loadtxt(dir_path + output_names[i], skiprows=6, delimiter=",")[:, :data_length]
    fig1_ax1.plot(IQ_data[0, :, i], IQ_data[1, :, i], label=labs[i])

# Read RF data
RF_data = np.loadtxt(dir_path + output_names[-1], skiprows=6, delimiter=",")
fig1_ax1.plot(RF_data[0,:], RF_data[1,:], label="RF - ISIM")

t_RX = IQ_data[0, ::8, 0]
t_TX = RF_data[0, ::8]
w = 2*np.pi*f_test
RX_phase = 5 * np.pi / 4
TX_phase = 5 * np.pi / 4


I_python = IQ_data.max() * np.sin(w * t_RX + RX_phase)
Q_python = IQ_data.max() * -np.cos(w * t_RX + RX_phase)
RF_python = RF_data.max() * np.sin(w * t_TX + TX_phase)

fig1_ax1.set_prop_cycle(None)

offset = {'RX_00': np.array([0.5, 1, 0.5])*1e-8, 'RX_11': np.array([0, 0, 0])*1e-8}

dataset_lbl = "RX_00"

fig1_ax1.plot(t_RX-offset[dataset_lbl][0], I_python, ".", label="I: sin($\omega t + 5\pi/4$)")
fig1_ax1.plot(t_RX-offset[dataset_lbl][1], Q_python, ".", label="Q: (-1)cos($\omega t + 5\pi/4$)")
fig1_ax1.plot(t_TX-offset[dataset_lbl][2], RF_python, ".", label="RF: sin($\omega t + 5\pi/4$)")

fig1_ax1.set_xlabel("t (s)")
fig1_ax1.set_ylabel("signal")
fig1_ax1.set_title("10MHz ISIM and Python outputs for signal_generator_tb.v\n"
                   "$\phi_{TX}$ = 00, $\phi_{RX} = 00$")
fig1_ax1.legend()
