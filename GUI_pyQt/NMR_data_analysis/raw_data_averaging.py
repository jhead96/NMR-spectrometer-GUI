import numpy as np
import os


def get_header(filename: str) -> str:
    header = ""
    return header


def get_data(filename: str) -> np.array:
    data = np.array([])
    return data


def save_processed_data(filename: str, data: np.array, header: str):
    pass


def main():

    # Get filenames in data directory
    dir_path = r""
    filenames = os.listdir(dir_path)

    header = ""
    n_files = len(filenames)
    n_datapoints = 65536
    accumulator = np.zeros((n_datapoints, 3))

    for f in filenames:

        # Get header and save file name
        if not header:
            header = get_header(f)

        # Add data to accumulator
        accumulator += get_data(f)

    # Calculate average
    mean_data = accumulator / n_files

    # Generate save file name
    save_name = ""

    # Save
    save_processed_data(save_name, mean_data, header)


main()