from scope_reader import ScopeReader

filepaths = ["scope_test_" + str(i+1) + ".csv" for i in range(4)]

for f in filepaths:
    data = ScopeReader(f)
    data.plot_intensity()

