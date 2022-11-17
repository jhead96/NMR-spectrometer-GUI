import raw_data_processor
import numpy as np

freqs = np.arange(213, 220, 0.5)
gaps = np.array([6, 10, 20, 50, 75, 100, 1000])
filenames = [f"G1_{str(g)}us" for g in gaps]
dirpath = r"X:\chungm-quantum-magnetism\PhD projects\Jake Head\NMR Data\Cobalt Powder\T1_inversion_recovery\\"
save_dirpath = r"X:\chungm-quantum-magnetism\PhD projects\Jake Head\NMR Data\Cobalt Powder\T1_processed_data\\"

save_names = [f + "_processed.txt" for f in filenames]
header_size = 9

for f, s in zip(filenames, save_names):
    print(f"Processing {f}")
    raw_data_processor.main(dirpath+f, save_dirpath+s, header_size)

