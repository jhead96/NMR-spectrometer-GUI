from scope_readers import TektronixReader

filepaths = [r"tektronix_scope_test_data/tektronix_scope_test_" + str(i+1) + ".csv" for i in range(4)]



for f in filepaths:
    data = TektronixReader(f)
    data.plot_intensity()

