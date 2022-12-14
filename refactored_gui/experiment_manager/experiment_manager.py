from data_handling.command import NMRCommand, PPMSCommand
from ..experiment_manager.sdr14_experiments import SDR14MultiRecordExperiment
from ..experiment_manager.ppms_experiments import PPMSWorker
from typing import Union
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal

class ExperimentManager(QObject):

    active_command = pyqtSignal(int)

    def __init__(self, spectrometer, PPMS) -> None:
        super().__init__()
        self.spectrometer = spectrometer
        self.PPMS = PPMS
        self.command_list = []
        self.command_counter = 0

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

    def start_experiment(self):
        self.command_counter = 0

        if not self.command_list:
            print("No commands in command list")
            return

        self.run_command()

    def run_command(self) -> None:

        if self.command_counter == len(self.command_list):
            print("Experiment finished!")
            return

        self.active_command.emit(self.command_counter)
        current_command = self.command_list[self.command_counter]

        if isinstance(current_command, NMRCommand):
            self.create_spectrometer_thread(current_command)
        else:
            self.create_PPMS_thread(current_command)

        self.command_counter += 1

    def create_spectrometer_thread(self, command: NMRCommand) -> None:
        self.thread = QThread()
        # Create Worker instance for spectrometer
        self.worker = SDR14MultiRecordExperiment(self.spectrometer, command, "test.txt")
        # Move worker to thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.thread.started.connect(self.worker.test_method)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        #worker.data_out.connect(plot_data)
        self.thread.destroyed.connect(self.run_command)
        #worker.expt_info.connect(update_expt_labels)
        self.thread.finished.connect(self.thread.deleteLater)
        # Start thread
        self.thread.start()

    def create_PPMS_thread(self, command: PPMSCommand) -> None:
        # Create QThread object
        self.thread = QThread()
        # Create Worker instance for PPMS
        self.worker = PPMSWorker(self.PPMS, command)
        # Move worker to thread
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.test_method)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        #worker.command_info.connect(self.update_expt_labels)
        #worker.parameters.connect(self.update_live_PPMS_plot)
        self.thread.destroyed.connect(self.run_command)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start thread
        self.thread.start()







