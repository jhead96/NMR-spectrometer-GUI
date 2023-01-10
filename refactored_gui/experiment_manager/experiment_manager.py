import numpy as np
from data_handling.command import NMRCommand, PPMSCommand
from ..experiment_manager.sdr14_experiments import SDR14MultiRecordExperiment
from ..experiment_manager.ppms_experiments import PPMSWorker
from ..experiment_manager.multithreading_instrument_classes import SpectrometerController, PPMSController
from typing import Union
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal


# noinspection PyUnresolvedReferences
class ExperimentManager(QObject):

    # NMR signals
    run_NMR_command = pyqtSignal(object)
    current_repeat = pyqtSignal(int)
    NMR_data = pyqtSignal(object, object, object, object)
    close_NMR_thread = pyqtSignal()
    # PPMS signals
    run_PPMS_command = pyqtSignal(object)
    close_PPMS_thread = pyqtSignal()
    # Progress signals
    curr_command = pyqtSignal(int)
    experiment_finished = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        # Initialize variables
        self.command_list = CommandList()
        self.active_command = 0
        self.ch1_accumulator = None
        self.ch2_accumulator = None
        # Make instrument threads
        self.NMR_thread, self.NMR_worker = self.create_NMR_thread()
        self.PPMS_thread, self.PPMS_worker = self.create_PPMS_thread()

    def create_NMR_thread(self) -> tuple[QThread, SpectrometerController]:
        thread = QThread()
        # Create Worker instance for spectrometer
        worker = SpectrometerController()
        worker.moveToThread(thread)
        # Connect signals
        worker.finished.connect(self.next_command)
        worker.current_repeat.connect(self.emit_repeat_to_gui)
        worker.data_out.connect(self.emit_NMR_data_to_gui)
        # Connect slots
        self.run_NMR_command.connect(worker.run_command)
        self.close_NMR_thread.connect(worker.close_thread)
        # Start thread
        thread.start()

        return thread, worker

    def create_PPMS_thread(self) -> tuple[QThread, PPMSController]:
        thread = QThread()
        # Create worker instance for PPMS
        worker = PPMSController()
        worker.moveToThread(thread)
        # Connect signals
        worker.finished.connect(self.next_command)
        # Connect slots
        self.run_PPMS_command.connect(worker.run_command)
        self.close_PPMS_thread.connect(worker.close_thread)
        # Start thread
        thread.start()

        return thread, worker

    def start_experiment(self) -> None:

        if not self.command_list.get_command_list():
            print("No commands in command list")
            self.experiment_finished.emit(-1)
            return
        self.generate_output_file()
        self.run_command()

    def run_command(self) -> None:

        # Check if experiment finished
        if self.active_command == len(self.command_list.get_command_list()):
            self.experiment_finished.emit(self.active_command-1)
            self.active_command = 0
            self.ch1_accumulator = None
            self.ch2_accumulator = None
            print("Experiment finished!")
            return

        self.curr_command.emit(self.active_command)
        current_command = self.command_list.get_command(self.active_command)

        if isinstance(current_command, NMRCommand):
            self.run_NMR_command.emit(current_command)
        else:
            self.run_PPMS_command.emit(current_command)

    def next_command(self) -> None:
        self.active_command += 1
        self.run_command()

    def emit_repeat_to_gui(self, repeat: int) -> None:
        self.current_repeat.emit(repeat)

    def emit_NMR_data_to_gui(self, rep: int, ch1_data: np.ndarray, ch2_data: np.ndarray) -> None:

        if self.ch1_accumulator is None:
            self.ch1_accumulator = np.zeros(ch1_data.size)
            self.ch2_accumulator = np.zeros(ch2_data.size)

        # Average data
        self.ch1_accumulator += ch1_data
        self.ch2_accumulator += ch2_data

        ch1_average = self.ch1_accumulator / rep
        ch2_average = self.ch2_accumulator / rep

        # Save data
        self.save_data_to_file(ch1_data, ch2_data)
        # Send data to plotting
        self.NMR_data.emit(ch1_data, ch2_data, ch1_average, ch2_average)

    def generate_output_file(self):


    def save_data_to_file(self, ch1_data, ch2_data):

    def close_threads(self):
        self.close_NMR_thread.emit()
        self.close_PPMS_thread.emit()

class CommandList(QObject):

    def __init__(self) -> None:
        super().__init__()
        self.command_list = []

    def delete_command(self, index: int) -> None:
        """
        Deletes a command from the command list.
        :param index: Index of command to be deleted.
        :return:
        """
        del self.command_list[index]

    def add_command(self, command: NMRCommand | PPMSCommand) -> None:
        """
        Appends a command to the command list.
        :param command: Command to be appended.
        :return:
        """
        self.command_list.append(command)

    def get_command_list(self) -> list[NMRCommand | PPMSCommand]:
        """
        Returns the command list.
        :return: command list object
        """
        return self.command_list

    def get_command(self, index: int) -> NMRCommand | PPMSCommand:
        """
        Gets the command from the command list at the specified index.
        :param index: Index of command to be returned.
        :return: command
        """
        return self.command_list[index]

    def get_command_type(self, index: int) -> type:
        """
        Returns the type of the command at the given index.
        :param index: Index of command type to be returned.
        :return: type of command
        """
        return type(self.command_list[index])

    def edit_command(self, index: int, repeats: None | int = None,
                     value: None | int = None, rate: None | int = None) -> None:
        """
        Edits the parameters of the command specified by the index.
        :param index: Index of command to be edited.
        :param repeats: If specified, sets the 'repeats' field of the selected command. Only works for NMRCommand.
        :param value: If specified, sets the 'value' field of the selected command. Only works for PPMSCommand.
        :param rate: If specified, sets the 'rate' field of the selected command. Only works for PPMSCommand.
        :return:
        """

        selected_command = self.command_list[index]

        if repeats:
            selected_command.set_repeats(repeats)
        if value:
            selected_command.edit_set_value(value)
        if rate:
            selected_command.set_rate(rate)






