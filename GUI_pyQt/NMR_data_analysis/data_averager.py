import raw_data_processor
import numpy as np

freqs = np.arange(213, 220, 0.5)
filenames = [f"{str(f).replace('.','pt')}_MHz" for f in freqs]
dirpath = r"X:\chungm-quantum-magnetism\PhD projects\Jake Head\NMR Data\Cobalt Powder\spectrum_raw_data\\"
save_dirpath = r"X:\chungm-quantum-magnetism\PhD projects\Jake Head\NMR Data\Cobalt Powder\spectrum_processed_data\\"

save_names = [f + "_processed.txt" for f in filenames]
header_size = 9

for f, s in zip(filenames, save_names):
    print(f"Processing {f}")
    raw_data_processor.main(dirpath+f, save_dirpath+s, header_size)

