import numpy as np
import os

def get_header(filename: str, header_size) -> str:
    header = ""
    line_count = 0

    with open(filename, "r") as f:
        for line in f.readlines():
            if line_count < header_size:
                header += line

            line_count += 1

    return header


def get_data(filename: str, header_size) -> np.array:
    data = np.loadtxt(filename, skiprows=header_size)
    return data


def save_processed_data(filename: str, data: np.array, header: str):
    np.savetxt(filename, data, header=header, comments="")


def main(dir_path: str, save_filename: str, header_size: int):

    # Get filepaths in data directory
    filepaths = [f"{dir_path}\\{i}" for i in os.listdir(dir_path)]
    header = ""
    header_size = 9
    n_files = len(filepaths)
    n_datapoints = 65536
    accumulator = np.zeros((n_datapoints, 3))
    count = 0

    for f in filepaths:
        print(f"Reading file {count+1}/{n_files}")
        # Get header and save file name
        if not header:
            header = get_header(f, header_size)

        # Add data to accumulator
        accumulator += get_data(f, header_size).T

        count += 1

    # Calculate average
    mean_data = accumulator / n_files

    # Save
    save_processed_data(save_filename, mean_data, header)


#main(r"X:\chungm-quantum-magnetism\PhD projects\Jake Head\NMR Data\Cobalt Powder\spectrum_raw_data\213pt0_MHz", "test.txt", 9)