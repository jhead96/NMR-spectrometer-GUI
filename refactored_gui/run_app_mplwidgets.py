from gui_mplwidgets_9 import *
from run_PPMS_command_window import *

import sys
import numpy as np
import scipy
import time
import os
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
from refactored_gui.plot_manager.plot_managers import MPLPlotManager

class RunApp(Ui_MainWindow):
    """
    Class to handle operation of the GUI on the main thread.
    """

    def __init__(self, window) -> None:

        # Setup GUI components
        self.setupUi(window)
        self.dialog = QtWidgets.QInputDialog()
        self.connect_button_functions()

        # Initialise active sample
        self.active_sample = None

        # Check for device connections
        self.spectrometer = SDR14()
        self.PPMS = PPMS()

        # Initialise plot manager
        canvs = {'time': self.timePlotWidget.canvas, 'fft': self.frqPlotWidget.canvas}
        ax_refs = {'time': self.timePlotWidget.canvas.ax, 'fft': self.frqPlotWidget.canvas.ax}
        self.plot_manager = MPLPlotManager(ax_refs, canvs)
        #self.initialise_plot_widgets()
        #self.time_plot_line = {"Channel A": None, "Channel B": None}
        #self.frq_plot_line = {"Channel A": None, "Channel B": None}

        # Initialise experiment manager
        self.expt_manager = ExperimentManager()

        # Signals from expt manager
        self.expt_manager.current_repeat.connect(self.update_expt_labels)
        self.expt_manager.curr_command.connect(self.change_treewidget_item_colour)
        self.expt_manager.experiment_finished.connect(self.reset_expt_tab)
        self.expt_manager.NMR_data.connect(self.update_plots)

        # Initialise default sequence and data filepaths
        self.default_seq_filepath = 'sequences\\'
        self.default_data_filepath = 'data\\'

        # Initialise data file cache
        self.data_file_cache = []

        # Initialise registers to be updated on FPGA
        self.registers = np.array([1, 2, 3, 5, 7])

        # Initialise command count and command count
        self.current_command = 0
        self.total_commands = 0

        self.num_parameters = 6

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
            self.show_dialog("Invalid sample name!")
        elif not new_sample.valid_mass:
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
            self.expt_manager.edit_command(item_index, value=value)
        if rate_valid:
            self.expt_manager.edit_command(item_index, rate=rate)

        # Update treewidget
        self.update_experiment_treewidget()

    def run_expt(self):
        self.startExptBtn.setDisabled(True)
        self.expt_manager.start_experiment()

    def change_treewidget_item_colour(self, index: int, reset: bool = False):


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

    def update_plots(self, ch1_data: np.ndarray, ch2_data: np.ndarray):
        self.plot_manager.update_plots(ch1_data, 'chA')
        self.plot_manager.update_plots(ch2_data, 'chB')

    def reset_expt_tab(self, last_index):
        """
        Resets the main tab after an experiment is finished.
        """

        self.startExptBtn.setDisabled(False)
        self.change_treewidget_item_colour(last_index, reset=True)

    def update_expt_labels(self, repeat='--'):
        """
        Updates the 'repeat' label during an experiment.
        """
        self.repeatValLbl.setText(f"{repeat}")

    def create_data_directory(self):
        """
        Creates a data folder to store the data files for the current sample.
        """

        # Construct directory path
        dir_path = self.default_data_filepath + self.sample_name

        # Check if sample name has been changed from default
        if self.sample_name != "":
            # Check if directory already exists
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        else:
            self.show_dialog("No sample name has been saved!")

    def create_data_file(self, seq_name, rep):
        """
        Creates a data file for a given sample and adds useful information to the header.
        """

        # Initialise loop variable
        i = 0

        # Reset data file cache
        self.data_file_cache = []

        # Repeat for number of repeats
        while i < rep:
            # Construct file path (data/sample name/sample name + seq name + expt number.txt)
            file_path = self.default_data_filepath + self.sample_name + '\\' + self.sample_name + '_' + seq_name + '_expt{}'.format(i+1) +'.txt'

            # Create data file
            f = open(file_path, "w+")

            # Write header
            f.write("[HEADER]\n")
            f.write(f"SAMPLE NAME,{self.sample_name}\n")
            f.write(f"SAMPLE MASS (mg),{self.sample_mass}\n")
            f.write(f"SAMPLE SHAPE,{self.sample_shape}\n")
            f.write(f"SEQUENCE,{seq_name}\n")
            f.write(f"EXPERIMENT NUMBER,{i+1}\n")
            f.write("[DATA]\n")
            f.close()

            i += 1

    def get_data_directory(self):
        """
        Gets a selected data directory and outputs the files within to the ComboBox on the 'Plot' tab.
        """
        # Get folder
        directory_path = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select data folder')
        # Update textbox
        self.currentDataFolder.setText(directory_path.split('/')[-1])

        # Read data files from folder
        data_filenames = os.listdir(directory_path)

        # Remove .txt for combo box display name
        display_names = []
        for filename in data_filenames:
            display_names.append(filename.split('.')[0])

        # Clear combo box
        self.datafileCombobox.clear()

        # Add names to combo box
        self.datafileCombobox.addItems(display_names)

    def plot_data(self):
        def get_data_filepath():
            """
            Constructs data file path from combobox selection.
            Returns: filepath
            """

            selected_filepath = '{}.txt'.format(self.datafileCombobox.currentText())
            filepath = self.default_data_filepath + self.currentDataFolder.text() + '\\' + selected_filepath
            return filepath

        def get_header_size(filepath):
            """
            Calculates the header size of a given data file.
            Returns: Header size
            """
            count = 0
            with open(filepath) as f:

                for line in f:
                    count += 1
                    if line == '[DATA]\n':
                        break

            header_size = count + 1

            return header_size

        def clear_widgets():
            """
            Clears both plot widgets.
            """

            self.timePlotWidget.canvas.ax.clear()
            self.timePlotWidget.canvas.draw()
            self.frqPlotWidget.canvas.ax.clear()
            self.frqPlotWidget.canvas.draw()

        def fourier_transform(data, fs):
            Ts = 1/fs
            N = data.size
            data_FFT = scipy.fft.fft(data)
            xf = scipy.fft.fftfreq(N, d=Ts)

            return xf, data_FFT


        # Clear plot widgets
        clear_widgets()
        # Get data filepath
        data_filepath = get_data_filepath()
        # Get header size
        skip_rows = get_header_size(data_filepath)
        # Read data from selected file
        data = np.loadtxt(data_filepath, delimiter=',', skiprows=skip_rows)
        # Calculate FFT frequencies and values for fs = 800MHz
        xf, data_FT = fourier_transform(data[:, 0], fs=800e6)
        N = data[:, 0].size


        # Plot Ch A time data to time widget
        self.timePlotWidget.canvas.ax.plot(data[:, 0])

        self.timePlotWidget.canvas.ax.set_ylabel('Signal')
        self.timePlotWidget.canvas.ax.set_title('Channel A Signal from SDR14')
        self.timePlotWidget.canvas.draw()

        # Plot Ch A FFT to frequency widget
        self.frqPlotWidget.canvas.ax.plot(xf[0:int(N/2)], np.abs(data_FT[0:int(N/2)]))

        self.frqPlotWidget.canvas.ax.set_xlabel('Frequency (Hz)')
        self.frqPlotWidget.canvas.ax.set_ylabel('Intensity')
        self.frqPlotWidget.canvas.ax.set_title('Spectrum')
        self.frqPlotWidget.canvas.draw()

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


def close_GUI():
    """
    Disconnects devices from the PC as the GUI is closed.
    """
    # Remove connection to SDR-14 if connected
    if ui.spectrometer is not None:
        ui.spectrometer.delete_control_unit()


app = QtWidgets.QApplication(sys.argv)
# Handle application close
app.aboutToQuit.connect(close_GUI)
MainWindow = QtWidgets.QMainWindow()
ui = RunApp(MainWindow)
MainWindow.show()
app.exec_()
