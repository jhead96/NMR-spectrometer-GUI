import numpy as np
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal


class SDR14MultiRecordExperiment(QObject):

    # Finished signal
    finished = pyqtSignal()
    # Data signal
    data_out = pyqtSignal(object, object)
    # Sequence and repeats signal
    expt_info = pyqtSignal(object, object)

    def __init__(self, device, command, data_filepath: str) -> None:
        super().__init__()
        self.device = device
        self.command = command
        self.parameters = command.sequence.convert_to_dict()
        self.data_filepath = data_filepath
        self.registers = []


    def test_method(self) -> None:

        print(f"NMR thread created with:\n"
              f"device = {self.device}\n"
              f"command = {self.command}\n"
              f"filepath = {self.data_filepath}")
        self.finished.emit()


    def run_expt(self) -> None:
        """
        Runs an experiment on the SDR14 using the parameters entered on the 'Experiment' tab of the GUI.
        Saves 1 record of data from the SDR14 using the MultiRecord mode to a text file.

        # Initialise k
        k = 0
        # Loop for number of repeats
        while k < self.num_reps:

            # Loop for each register
            for j in self.reg_vals:
                # Write data to SDR14 register
                self.device.reg_write(*j)

            # Emit expt info
            self.expt_info.emit(self.seq_name, k + 1)

            # Enable device
            self.device.enable_dev()

            # Start MR acquisition
            ch1_data, ch2_data = self.device.MR_acquisition()
            # Save to file
            data_filepath = f'{self.data_filepath}_expt{k + 1}.txt'
            self.save_data_to_file(data_filepath, ch1_data, ch2_data)

            print(f'Sequence name: {self.seq_name}')
            print(f'Experiment number: {k+1}')
            print(f'Data file path: {data_filepath}')

            time.sleep(2)

            # Disable device
            self.device.disable_dev()
            print('Device disabled')
            print('')
            print('')
            time.sleep(2)
            # Increment k
            k += 1

        print(f'NMR Spectrometer worker thread: Sequence {self.seq_name} finished!')
        # Emit finished signal
        self.finished.emit()
        """

    @staticmethod
    def save_data_to_file(filepath: str, ch1_data: np.ndarray[float], ch2_data: np.ndarray[float]) -> None:
        """
        Saves data from the SDR14 to a text file.
        """
        save_data = np.stack((ch1_data, ch2_data), axis=1)

        with open(filepath, "ab") as f:
            np.savetxt(f, save_data, header='Ch 1 data, Ch 2 data', comments='', delimiter=',')
            f.close()

