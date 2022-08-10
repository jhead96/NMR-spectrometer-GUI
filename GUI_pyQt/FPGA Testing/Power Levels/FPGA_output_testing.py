from scope_reader import ScopeReader

freqs = ["0pt5", 1, 10, 100, 200, 300, 400]

filenames = ["FPGA_output_" + str(i) + "MHz.csv" for i in freqs]


for f in filenames:
    data = ScopeReader(f)
    data.plot_data()