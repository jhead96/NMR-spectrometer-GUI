from gui_pyqtgraph_11 import *
from run_PPMS_command_window import *

import sys
import numpy as np
import scipy
import time
import os
import logging
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QBrush, QColor

# Instrument controllers
from instrument_controllers.sdr14_controller import SDR14
from instrument_controllers.ppms_controller import PPMS

# Data handling objects
from data_handling.sample import Sample
from data_handling.sequence import Sequence
from data_handling.command import NMRCommand, PPMSFieldCommand, PPMSTemperatureCommand

# Experiment management
from refactored_gui.experiment_manager.experiment_manager import ExperimentManager
# Plot management
from refactored_gui.plot_manager.plot_managers import PyqtgraphPlotManager


class RunApp(Ui_MainWindow):
    """
    Class to handle operation of the GUI on the main thread.
    """

    def __init__(self, window) -> None:
        # Initialise logger
        self.logger = self.initialise_logger()

        # Setup GUI components
        self.setupUi(window)
        self.dialog = QtWidgets.QInputDialog()
        self.connect_button_functions()

        # Initialise active sample
        self.active_sample = None

        # Initialise plot manager
        plot_widgets = {'average_time': self.averageTimePlotWidget, 'last_time': self.lastTimePlotWidget}
        self.plot_manager = PyqtgraphPlotManager(plot_widgets)

        # Initialise experiment manager
        self.expt_manager = ExperimentManager()

        # Signals from expt manager
        self.expt_manager.current_repeat.connect(self.update_expt_labels)
        self.expt_manager.curr_command.connect(self.change_treewidget_item_colour)
        self.expt_manager.experiment_finished.connect(self.reset_expt_tab)
        self.expt_manager.NMR_data.connect(self.update_plot)
        self.expt_manager.PPMS_data_to_gui.connect(self.update_PPMS_condition_labels)

        # Initialise default sequence filepath
        self.default_seq_filepath = 'sequences\\'

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

    def connect_button_functions(self) -> None:
        """
        Connects functions to button click events
        :return:
        """

        # Sample tab
        self.confirmSampleInfoBtn.clicked.connect(self.get_sample_info)
        self.clearSampleInfoBtn.clicked.connect(self.clear_sample_info)

        # Sequence tab
        self.clearAllBtn.clicked.connect(self.clear_seq_line_edits)
        self.loadSeqBtn.clicked.connect(self.load_seq_file)
        self.saveSeqBtn.clicked.connect(self.save_seq_file)

        # Experiment tab
        self.addNMRCommandBtn.clicked.connect(self.add_NMR_command)
        self.addPPMSCommandBtn.clicked.connect(self.add_PPMS_command)
        self.removeCommandBtn.clicked.connect(self.remove_command)
        self.editCommandBtn.clicked.connect(self.edit_command)
        self.startExptBtn.clicked.connect(self.run_expt)
        self.saveDirBtn.clicked.connect(self.set_save_dir)

    def initialise_plot_widgets(self) -> None:
        """
        Initialises figure and axes for plotting.
        :return:
        """

        # Assign axes to variables
        time_plot_ax = self.timePlotWidget.canvas.ax
        frq_plot_ax = self.frqPlotWidget.canvas.ax

        # Initialise time plot axes
        time_plot_ax.set_title('Signal from SDR14')
        time_plot_ax.set_xlabel('Sample number')
        time_plot_ax.set_ylabel('Signal')

        # Initialise frq plot axes
        frq_plot_ax.set_title('Spectrum')
        frq_plot_ax.set_xlabel('Frequency (Hz)')
        frq_plot_ax.set_ylabel('Intensity (arb.)')

    def get_sample_info(self) -> None:
        """
        Updates active sample from information in the sample tab
        :return:
        """
        # Read sample information from text-boxes
        name = self.sampleNameLineEdit.text()
        mass = self.sampleMassLineEdit.text()
        shape = self.sampleShapeLineEdit.text()

        # Make new sample
        new_sample = Sample(name, mass, shape)

        # Check validity of fields
        if not new_sample.valid_name:
            self.logger.warning("Invalid sample name")
            self.show_dialog("Invalid sample name!")

        elif not new_sample.valid_mass:
            self.logger.warning("Invalid sample mass")
            self.show_dialog("Invalid sample mass!")
        else:
            self.active_sample = new_sample
            self.currentSampleNameLbl.setText(f'Current sample name: {self.active_sample.name}')
            self.currentSampleMassLbl.setText(f'Current sample mass: {self.active_sample.mass} mg')
            self.currentSampleShapeLbl.setText(f'Current sample shape: {self.active_sample.shape}')

    def clear_sample_info(self) -> None:
        """
        Clears active sample info from the class.
        :return:
        """
        # Reset internal sample variables
        self.active_sample = None
        # Reset labels
        self.currentSampleNameLbl.setText('Current sample name: No sample entered!')
        self.currentSampleMassLbl.setText('Current sample mass: No sample entered!')
        self.currentSampleShapeLbl.setText('Current sample shape: No sample shape!')
        # Clear textboxes
        self.sampleNameLineEdit.setText("")
        self.sampleMassLineEdit.setText("")
        self.sampleShapeLineEdit.setText("")
        self.logger.debug("Active sample cleared")

    # noinspection PyTypeChecker
    def save_seq_file(self) -> None:
        """
        Saves sequence values from the 'Sequence' tab into a .seq file.
        :return:
        """

        # Get save data filepath using windows dialog
        save_filename = self.get_filepath_from_dialog()
        # Combine data from text-boxes into array
        save_data = np.array([self.frequencyLineEdit.text(), self.txPhaseComboBox.currentText(),
                              self.rxPhaseComboBox.currentText(), self.pulse1LenLineEdit.text(),
                              self.gapLenLineEdit.text(), self.pulse2LenLineEdit.text(),
                              self.gap2LenLineEdit.text(), self.pulse3LenLineEdit.text(),
                              self.recLenLineEdit.text()])

        # Make Sequence object
        seq = Sequence(*save_data)
        # Set name
        seq.set_name(save_filename.split('/')[-1][:-4])
        # Save data
        if seq.valid_sequence:
            seq.save_to_file(save_filename)
            # Update saved file text-box
            self.savedSeqLineEdit.setText(save_filename)
        else:
            self.show_dialog("Invalid sequence parameters!")

    def load_seq_file(self) -> None:
        """
        Loads values from the designated sequence file into the 'Sequence' tab for editing.
        :return:
        """

        def set_combo_box(combo_box, phase: int):
            if phase == 0:
                combo_box.setCurrentIndex(0)
            elif phase == 90:
                combo_box.setCurrentIndex(1)
            elif phase == 180:
                combo_box.setCurrentIndex(2)
            elif phase == 270:
                combo_box.setCurrentIndex(3)

        # Open file dialog
        load_filepath = QtWidgets.QFileDialog.getOpenFileName(None, "Open sequence", self.default_seq_filepath)
        # Read file name of sequence
        load_filename = load_filepath[0].split('/')[-1]
        # Set loaded file textbox
        self.loadedSeqLineEdit.setText(load_filename)
        # Load data
        seq_data = np.loadtxt(load_filepath[0]).astype(np.int64)
        loaded_seq = Sequence(*seq_data)
        # Move values from file into text-boxes
        self.frequencyLineEdit.setText(str(loaded_seq.frequency))
        self.pulse1LenLineEdit.setText(str(loaded_seq.p1))
        self.gapLenLineEdit.setText(str(loaded_seq.g1))
        self.pulse2LenLineEdit.setText(str(loaded_seq.p2))
        self.gap2LenLineEdit.setText(str(loaded_seq.g2))
        self.pulse3LenLineEdit.setText(str(loaded_seq.p3))
        self.recLenLineEdit.setText(str(loaded_seq.rec))
        # Set phase combo boxes
        set_combo_box(self.txPhaseComboBox, loaded_seq.TX_phase)
        set_combo_box(self.rxPhaseComboBox, loaded_seq.RX_phase)

    def clear_seq_line_edits(self) -> None:
        """
        Clears all text-boxes on the 'Sequence' tab.
        :return:
        """
        # Clear all text boxes
        self.frequencyLineEdit.setText('')
        self.pulse1LenLineEdit.setText('')
        self.pulse2LenLineEdit.setText('')
        self.pulse3LenLineEdit.setText('')
        self.gapLenLineEdit.setText('')
        self.gap2LenLineEdit.setText('')
        self.recLenLineEdit.setText('')
        self.savedSeqLineEdit.setText('')
        self.loadedSeqLineEdit.setText('')
        # Reset phase combo boxes
        self.txPhaseComboBox.setCurrentIndex(0)
        self.rxPhaseComboBox.setCurrentIndex(0)

    def update_experiment_treewidget(self) -> None:
        """
        Updates the Experiment TreeWidget to display all commands in the experiment manager.
        :return:
        """

        # Clear treewidget
        self.exptTreeWidget.clear()

        command_list = self.expt_manager.command_list.get_command_list()
        print(command_list)
        # Repopulate treewidget
        for com in command_list:
            # If command is NMRCommand
            if isinstance(com, NMRCommand):
                item = QtWidgets.QTreeWidgetItem(self.exptTreeWidget, [com.command_type, com.sequence_filepath, str(com.repeats)])
            # Else command is PPMSCommand
            else:
                item = QtWidgets.QTreeWidgetItem(self.exptTreeWidget, [com.command_type, com.command_lbl, "--"])

            # Add item
            self.exptTreeWidget.addTopLevelItem(item)

    def add_NMR_command(self) -> None:
        """
        Adds an NMR command to the Experiment TreeWidget.
        :return:
        """
        # Open file dialog
        load_filepath = QtWidgets.QFileDialog.getOpenFileName(None, "Open sequence", self.default_seq_filepath)
        # Read file name of sequence
        load_filename = load_filepath[0].split('/')[-1][:-4]

        if load_filename:
            # Get number of repeats
            repeats, _ = QtWidgets.QInputDialog.getInt(self.dialog, 'Repeats', 'Enter number of repeats', 1, 1 )

            # Make new command
            command = NMRCommand(load_filepath[0], repeats)

            if command.valid_command:
                # Add command to manager
                self.expt_manager.command_list.add_command(command)
                self.update_experiment_treewidget()

            else:
                self.show_dialog('Invalid entry!')

    def add_PPMS_command(self) -> None:
        """
        Adds a PPMS command to the Experiment TreeWidget.
        :return:
        """

        def generate_PPMS_command(parameter: str, value: float, rate: float) -> None:
            """
            Generates a new PPMS command using the data provided in the PPMS data window.
            :param parameter: Type of Command either "Temperature" or "Magnetic Field".
            :param value: Set value for the command.
            :param rate: Rate to be used.
            :return:
            """
            self.ppms_window.destroy()

            if parameter == "Temperature":
                new_command = PPMSTemperatureCommand(value, rate)
            else:
                new_command = PPMSFieldCommand(value, rate)

            self.expt_manager.command_list.add_command(new_command)
            self.update_experiment_treewidget()


        # Bring up PPMS command window
        self.ppms_window = QtWidgets.QMainWindow()
        self.ui = runPPMSCommandWindow(self.ppms_window)
        self.ui.PPMS_parameters.connect(generate_PPMS_command)
        self.ppms_window.show()

    def remove_command(self) -> None:
        """
        Removes the selected command from the Experiment TreeWidget.
        """
        # Check for selected items
        selected_item = self.exptTreeWidget.selectedItems()
        # If an item is selected
        if selected_item:
            # Get selected node
            base_node = selected_item[0]
            # Get index of selected node
            index = self.exptTreeWidget.indexFromItem(base_node).row()
            # Delete selected node
            self.expt_manager.command_list.delete_command(index)
            # Refresh tree widget
            self.update_experiment_treewidget()

    def edit_command(self) -> None:
        """
        Edits the number of repeats or the set value and rate of a selected command.
        :return:
        """

        # Check for selected item
        selected_item = self.exptTreeWidget.selectedItems()[0]

        if not selected_item:
            return

        item_index = self.exptTreeWidget.indexOfTopLevelItem(selected_item)
        command_type = self.expt_manager.command_list.get_command_type(item_index)

        value = None
        rate = None
        value_valid = None
        rate_valid = None

        # If NMRCommand
        if command_type is NMRCommand:
            repeats, valid = QtWidgets.QInputDialog.getInt(self.dialog, 'Repeats', 'Enter number of repeats', 1, 1)
            if valid:
                self.expt_manager.command_list.edit_command(item_index, repeats=repeats)

        # If PPMSTemperatureCommand
        elif command_type is PPMSTemperatureCommand:
            value, value_valid = QtWidgets.QInputDialog.getDouble(self.dialog, 'Edit temperature',
                                                                  'Enter temperature (2K - 400K)',
                                                                  min=2, max=400, decimals=3)

            rate, rate_valid = QtWidgets.QInputDialog.getDouble(self.dialog, 'Edit rate',
                                                                'Enter temperature rate (2K/s - 20K/s)',
                                                                min=2, max=20, decimals=3)
        # If PPMSFieldCommand
        else:
            value, value_valid = QtWidgets.QInputDialog.getDouble(self.dialog, 'Edit magnetic field',
                                                            'Enter magnetic field (-70,000Oe - 70,000Oe)', min=-70000, max=70000, decimals=3)
            rate, rate_valid = QtWidgets.QInputDialog.getDouble(self.dialog, 'Edit rate',
                                                            'Enter magnetic field rate (10Oe/s - 500Oe/s)', min=10, max=500, decimals=3)

        # Set PPMSCommand parameters
        if value_valid:
            self.expt_manager.command_list.edit_command(item_index, value=value)
        if rate_valid:
            self.expt_manager.command_list.edit_command(item_index, rate=rate)

        # Update treewidget
        self.update_experiment_treewidget()

    def run_expt(self) -> None:
        self.startExptBtn.setDisabled(True)
        self.saveDirBtn.setDisabled(True)
        self.expt_manager.set_current_sample(self.active_sample)
        self.expt_manager.start_experiment()

    def change_treewidget_item_colour(self, index: int, reset: bool = False) -> None:


        # Define brushes
        brushes = {'active': QBrush(QColor("#00FF00")), 'inactive': QBrush(QColor("#000000"))}

        # Get current command
        curr_item = self.exptTreeWidget.topLevelItem(index)

        # If reset change item to black
        if reset:
            curr_item.setForeground(0, brushes['inactive'])
            curr_item.setForeground(1, brushes['inactive'])
            curr_item.setForeground(2, brushes['inactive'])
            return

        # Set current command to green
        curr_item.setForeground(0, brushes['active'])
        curr_item.setForeground(1, brushes['active'])
        curr_item.setForeground(2, brushes['active'])

        # Set previous command to black
        if index != 0:
            prev_item = self.exptTreeWidget.topLevelItem(index - 1)


            prev_item.setForeground(0, brushes['inactive'])
            prev_item.setForeground(1, brushes['inactive'])
            prev_item.setForeground(2, brushes['inactive'])

    def update_plot(self, ch1_data: np.ndarray, ch2_data: np.ndarray, ch1_average: np.ndarray, ch2_average: np.ndarray):

        self.plot_manager.update_plot(ch1_data, 'last_time', 'ch1')
        self.plot_manager.update_plot(ch2_data, 'last_time', 'ch2')

        self.plot_manager.update_plot(ch1_average, 'average_time', 'ch1')
        self.plot_manager.update_plot(ch2_average, 'average_time', 'ch2')

    def reset_expt_tab(self, last_index: int) -> None:
        """
        Resets the main tab after an experiment is finished.
        """

        self.startExptBtn.setDisabled(False)
        self.saveDirBtn.setDisabled(False)
        # Handle any early exit
        if last_index == -1:
            self.show_dialog("No commands in experiment!")
            self.logger.warning("No commands in experiment")
            return
        if last_index == -2:
            self.show_dialog("No output directory selected!")
            self.logger.warning("No output directory selected")
            return

        self.change_treewidget_item_colour(last_index, reset=True)
        self.logger.info("GUI reset")

    def update_expt_labels(self, repeat: str | int = '--') -> None:
        """
        Updates the 'repeat' label during an experiment.
        """
        self.repeatValLbl.setText(f"{repeat}")

    def update_PPMS_condition_labels(self, T: float, H: float) -> None:
        self.tempValLbl.setText(f"{T:.3}")
        self.fieldValLbl.setText(f"{H:.3}")

    def set_save_dir(self) -> None:
        save_dir = QtWidgets.QFileDialog.getExistingDirectory()

        if save_dir:
            self.currentDataDirLineEdit.setText(save_dir.split('/')[-1])
            self.expt_manager.set_output_directory(save_dir)
        else:
            self.warning("No output directory selected")
            self.show_dialog("No output directory selected!")
            return ""

    def show_dialog(self, msg_text: str) -> None:
        """
        Convenience function to show a warning dialog with custom text.
        """

        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg_text)
        msgbox.setWindowTitle("Warning")
        msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgbox.exec()

    def get_filepath_from_dialog(self, filt: str ="seq files (*.seq)") -> str:

        filepath = QtWidgets.QFileDialog.getSaveFileName(filter=filt)[0]

        if filepath:
            return filepath
        else:
            self.show_dialog("No filepath selected!")
            return ""

    def shutdown_app(self) -> None:
        self.logger.info("Closing application")
        self.expt_manager.close_threads()

def close_GUI():
    """
    Disconnects devices from the PC as the GUI is closed.
    """
    # Remove connection to SDR-14 if connected
    ui.shutdown_app()


app = QtWidgets.QApplication(sys.argv)
# Handle application close
app.aboutToQuit.connect(close_GUI)
MainWindow = QtWidgets.QMainWindow()
ui = RunApp(MainWindow)
MainWindow.show()
app.exec_()
