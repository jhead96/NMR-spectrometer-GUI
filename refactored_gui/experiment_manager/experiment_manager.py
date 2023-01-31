import numpy as np
import os
import logging
from datetime import datetime
from data_handling.command import NMRCommand, PPMSCommand
from ..experiment_manager.sdr14_experiments import SDR14MultiRecordExperiment
from ..experiment_manager.ppms_experiments import PPMSWorker
from ..experiment_manager.multithreading_instrument_classes import SpectrometerControllerDummy, PPMSControllerDummy
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal


# noinspection PyUnresolvedReferences
class ExperimentManager(QObject):

    # NMR signals
    run_NMR_command = pyqtSignal(object)
    current_repeat = pyqtSignal(int)
    NMR_data = pyqtSignal(object, object, object, object)
    set_NMR_output_path = pyqtSignal(str)
    close_NMR_thread = pyqtSignal()
    # PPMS signals
    run_PPMS_command = pyqtSignal(object)
    set_PPMS_output_path = pyqtSignal(str)
    get_PPMS_conditions = pyqtSignal(str)
    PPMS_data_to_gui = pyqtSignal(float, float)
    close_PPMS_thread = pyqtSignal()
    # Progress signals
    curr_command = pyqtSignal(int)
    experiment_finished = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        # Initialise logger
        self.logger = self.initialise_logger()
        # Initialise variables
        self.command_list = CommandList()
        self.active_command = 0
        self.output_directory = None
        self.current_sample = None
        self.ch1_accumulator = None
        self.ch2_accumulator = None
        # Make instrument threads
        self.NMR_thread, self.NMR_worker = self.create_NMR_thread()
        self.PPMS_thread, self.PPMS_worker = self.create_PPMS_thread()
        # Flags for closing threads
        self.NMR_safe_to_close = False
        self.PPMS_safe_to_close = False

    @staticmethod
    def initialise_logger() -> logging.Logger:

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Log formatting
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(log_format, date_format)

        # File logging
        file_handler = logging.FileHandler("logs.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        # Console logging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)

        return logger

    def create_NMR_thread(self) -> tuple[QThread, SpectrometerControllerDummy]:
        thread = QThread()
        # Create Worker instance for spectrometer
        worker = SpectrometerControllerDummy()
        worker.moveToThread(thread)
        self.logger.info("NMR worker thread created")
        # Connect signals
        worker.finished.connect(self.next_command)
        worker.current_repeat.connect(self.emit_repeat_to_gui)
        worker.data_out.connect(self.emit_NMR_data_to_gui)
        # Connect slots
        self.run_NMR_command.connect(worker.run_command)
        self.set_NMR_output_path.connect(worker.set_save_dir)
        self.close_NMR_thread.connect(worker.shutdown_thread)
        # Start thread
        thread.start()


        return thread, worker

    def create_PPMS_thread(self) -> tuple[QThread, PPMSControllerDummy]:
        thread = QThread()
        # Create worker instance for PPMS
        worker = PPMSControllerDummy()
        worker.moveToThread(thread)
        self.logger.info("PPMS worker thread created")
        # Connect signals
        worker.finished.connect(self.next_command)
        worker.PPMS_data_out.connect(self.emit_PPMS_data_to_gui)
        # Connect slots
        self.run_PPMS_command.connect(worker.run_command)
        self.set_PPMS_output_path.connect(worker.set_save_dir)
        self.get_PPMS_conditions.connect(worker.poll_PPMS)
        self.close_PPMS_thread.connect(worker.shutdown_thread)
        # Start thread
        thread.start()

        return thread, worker

    def start_experiment(self) -> None:

        if not self.command_list.get_command_list():
            self.logger.warning("No commands in command list")
            self.experiment_finished.emit(-1)
            return

        if not self.output_directory:
            self.logger.warning("No output directory selected")
            self.experiment_finished.emit(-2)
            return

        self.logger.info(f"Experiment starting with sample {self.current_sample}")
        path = self.generate_output_directory()
        self.generate_info_file(path)
        self.run_command()

    def run_command(self) -> None:

        # Check if experiment finished
        if self.active_command == len(self.command_list.get_command_list()):
            self.experiment_finished.emit(self.active_command-1)
            self.active_command = 0
            self.ch1_accumulator = None
            self.ch2_accumulator = None
            self.logger.info("Experiment finished")
            return

        self.curr_command.emit(self.active_command)
        current_command = self.command_list.get_command(self.active_command)
        self.logger.info(f"Starting command: {current_command}")

        if isinstance(current_command, NMRCommand):
            self.run_NMR_command.emit(current_command)
        else:
            self.run_PPMS_command.emit(current_command)

    def next_command(self) -> None:
        # Reset accumulators
        self.ch1_accumulator = None
        self.ch2_accumulator = None
        # Increment command
        self.active_command += 1
        # Run
        self.run_command()

    def emit_repeat_to_gui(self, repeat: int, seq_name: str) -> None:
        self.current_repeat.emit(repeat)
        # Poll PPMS
        self.logger.debug(seq_name)
        self.get_PPMS_conditions.emit(seq_name)

    def emit_NMR_data_to_gui(self, rep: int, ch1_data: np.ndarray, ch2_data: np.ndarray, save_dir: str) -> None:

        if self.ch1_accumulator is None:
            self.ch1_accumulator = np.zeros(ch1_data.size)
            self.ch2_accumulator = np.zeros(ch2_data.size)

        # Average data
        self.ch1_accumulator += ch1_data
        self.ch2_accumulator += ch2_data

        ch1_average = self.ch1_accumulator / rep
        ch2_average = self.ch2_accumulator / rep

        # Get current command
        current_command = self.command_list.get_command(self.active_command)
        seq_name = current_command.sequence_filepath.split('/')[-1][:-4]

        # Save data
        np.savetxt(f"{save_dir}/{seq_name}_avg.txt", (ch1_average, ch2_average))
        # Send data to plotting
        self.NMR_data.emit(ch1_data, ch2_data, ch1_average, ch2_average)

    def emit_PPMS_data_to_gui(self, T: float, H: float) -> None:
        self.PPMS_data_to_gui.emit(T, H)

    def set_current_sample(self, sample) -> None:
        self.current_sample = sample
        self.logger.debug(f"Set active sample to {sample}")

    def set_output_directory(self, directory: str) -> None:
        self.output_directory = directory
        self.logger.debug(f"Set output directory to {directory}")

    def generate_output_directory(self) -> str:

        if self.current_sample is None:
            dir_name = "Unnamed sample"
        else:
            dir_name = self.current_sample.name

        full_output_path = f"{self.output_directory}/{dir_name}"

        # Make new dir and handle duplicate name
        valid = False
        while not valid:
            try:
                os.mkdir(full_output_path)
            except FileExistsError as ex:
                if "_" not in dir_name:
                    dir_name += "_1"
                else:
                    temp_name, version = dir_name.split("_")
                    dir_name = f"{temp_name}_{int(version) + 1}"
                    full_output_path = f"{self.output_directory}/{dir_name}"
            else:
                valid = True

        # Send output path to threads
        self.set_NMR_output_path.emit(full_output_path)
        self.set_PPMS_output_path.emit(full_output_path)

        self.logger.info(f"Output directory generated: {full_output_path}")

        return full_output_path

    def generate_info_file(self, path) -> None:

        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H:%M:%S")

        command_list = self.command_list.get_command_list()
        command_str = "COMMAND LIST, " + "".join([f"{com}\t" for com in command_list])

        with open(f"{path}/info.txt", 'w') as f:
            f.write(f"START TIME, {timestamp}\n")
            if self.current_sample:
                f.write(f"SAMPLE NAME, {self.current_sample.name}\n")
                f.write(f"SAMPLE MASS (mg), {self.current_sample.mass}\n")
                f.write(f"SAMPLE SHAPE, {self.current_sample.shape}\n")
            f.write(command_str)

        self.logger.info(f"Info file created at {path}/info.txt")

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






