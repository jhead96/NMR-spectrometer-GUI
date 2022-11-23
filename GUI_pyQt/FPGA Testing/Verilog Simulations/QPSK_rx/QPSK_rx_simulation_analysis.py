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


data = np.zeros((2, 800, 2))
labs = ["I - ISIM", "Q - ISIM"]
phase = [5*np.pi/4, 3*np.pi/4, np.pi/4, 7*np.pi/4]
phase_lbl = ["$5\pi/4$", "$3\pi/4$", "$\pi/4$", "$7\pi/4$"]
phase_str = ["0", "90", "180", "270"]
phase_bin = ["00", "01", "11", "10"]
w = 2*np.pi*f_test

I_savenames = [f"{dir_path}10MHz_phase_{p}_I_decimal.txt" for p in phase_str]
Q_savenames = [f"{dir_path}10MHz_phase_{p}_Q_decimal.txt" for p in phase_str]


# Read data and plot
for i in range(0, 4):
    I_data = np.loadtxt(I_savenames[i], skiprows=5, delimiter=",")
    Q_data = np.loadtxt(Q_savenames[i], skiprows=5, delimiter=",")


    plt.plot(I_data[0, :], I_data[1, :], label=labs[0])
    plt.plot(Q_data[0, :], Q_data[1, :], label=labs[1])


    t = I_data[0, ::8]

    I_python = I_data.max() * np.sin(w*t + phase[i])
    Q_python = Q_data.max() * np.cos(w*t + phase[i])

    plt.gca().set_prop_cycle(None)
    plt.plot(t, I_python, ".", label=f"I - sin($\omega t$ + {phase_lbl[i]})")
    plt.plot(t, Q_python, ".", label=f"Q - cos($\omega t$ + {phase_lbl[i]})")

    plt.xlabel("t (s)")
    plt.ylabel("signal")
    plt.title(f"16-bit, 10MHz Verilog output for $\phi_{{rx}}$ = '{phase_bin[i]}'")
    plt.legend()
    plt.figure()
