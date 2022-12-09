from gui_8 import *
from run_PPMS_command_window import *

import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy
import time
import os
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QBrush, QColor

# Instrument controllers
from instrument_controllers.sdr14_controller import SDR14
from instrument_controllers.ppms_controller import PPMS

# Data handling objects
from data_handling.sample import Sample
from data_handling.sequence import Sequence
from data_handling.command import NMRCommand, PPMSCommand, PPMSFieldCommand, PPMSTemperatureCommand
from data_handling import *

# Experiment management
from experiment_manager import ExperimentManager




# noinspection PyUnresolvedReferences
class SpecMRWorker(QObject):
    """
    Class to handle interfacing with the SDR14 on a Worker thread.
    """

    # Finished signal
    finished = pyqtSignal()
    # Data signal
    data_out = pyqtSignal(object, object)
    # Sequence and repeats signal
    expt_info = pyqtSignal(object, object)

    def __init__(self, device, reg_vals, num_reps, data_filepath, seq_name):
        super().__init__()
        self.device = device
        self.reg_vals = reg_vals
        self.num_reps = int(num_reps)
        self.num_seqs = np.size(num_reps)
        self.data_filepath = data_filepath
        self.seq_name = seq_name

    def run_expt(self):
        """
        Runs an experiment on the SDR14 using the parameters entered on the 'Experiment' tab of the GUI.
        Saves 1 record of data from the SDR14 using the MultiRecord mode to a text file.
        """
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

    def save_data_to_file(self, filepath, ch1_data, ch2_data):
        """
        Saves data from the SDR14 to a text file.
        """
        save_data = np.stack((ch1_data, ch2_data), axis=1)

        with open(filepath, "ab") as f:
            np.savetxt(f, save_data, header='Ch 1 data, Ch 2 data', comments='', delimiter=',')
            f.close()


class SpecLiveWorker(QObject):
    """
    Class to handle continuous data acquisition from SDR 14 on worker thread.
    """
    # Signals
    finished = pyqtSignal()
    # Data out signal
    data_out = pyqtSignal(object, object)

    def __init__(self, device, reg_vals):
        super().__init__()
        self.device = device
        self.reg_vals = reg_vals
        self.enabled = True

    def continuous_acquisition(self):
        """
        Function used to continuously acquire data from SDR14.
        """
        # Write register values
        for i in self.reg_vals:
            self.device.reg_write(*i)
        # Enable device
        self.device.enable_dev()

        # Run loop until device disabled
        while self.enabled:

            ch1_data, ch2_data = self.device.MR_acquisition()
            self.data_out.emit(ch1_data, ch2_data)

    def stop_acquisition(self):
        """
        Stops the data acquisition from the SDR14.
        """

        self.enabled = False
        self.device.disable_dev()
        self.finished.emit()


class PPMSWorker(QObject):
    # Finished signal
    finished = pyqtSignal()
    # Command info signal
    command_info = pyqtSignal(object)
    # Parameters signal
    parameters = pyqtSignal(float, float)


    def __init__(self, parameter, value, rate, start_time=0):
        super().__init__()
        self.parameter = parameter
        self.value = value
        self.rate = rate
        self.starting_value = 300.00
        self.start_time = start_time

    def set_value(self):

        if self.parameter == 'T':
            self.command_info.emit(f'\nSet temp. to {self.value}K.\n Rate {self.rate}K/s. ')

            curr_val = self.starting_value
            t = self.start_time
            val_float = float(self.value)
            rate_float = float(self.rate)
            print(val_float <= curr_val)

            while val_float <= curr_val:

                curr_val -= rate_float
                t += 1
                #print(f'T={curr_val}K, t={t}s')
                self.parameters.emit(t, curr_val)
                time.sleep(1)

            print(f'PPMS worker thread: Setting temp to {self.value}K finished!')

        else:
            self.command_info.emit(f'Setting field to {self.value}Oe at rate {self.rate}Oe/s ')
            time.sleep(1)



            print(f'PPMS worker thread: Setting field to {self.value}Oe finished!')

        self.finished.emit()


class RunApp(Ui_MainWindow):
    """
    Class to handle operation of the GUI on the main thread.
    """

    def __init__(self, window) -> None:

        # Setup GUI components
        self.setupUi(window)
        self.dialog = QtWidgets.QInputDialog()
        self.connect_button_functions()

        # Setup graph widgets
        self.initialise_plot_widgets()
        self.time_plot_line = {"Channel A": None, "Channel B": None}
        self.frq_plot_line = {"Channel A": None, "Channel B": None}

        # Initialise active sample
        self.active_sample = None

        # Check for device connections
        self.spectrometer = SDR14()
        self.PPMS = PPMS()

        # Initialise default sequence and data filepaths
        self.default_seq_filepath = 'sequences\\'
        self.default_data_filepath = 'data\\'

        # Initialise manager for experiment
        self.expt_manager = ExperimentManager()

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
        save_data = np.array([self.frequencyLineEdit.text(), "90", "180",
                              self.pulse1LenLineEdit.text(), self.gapLenLineEdit.text(), self.pulse2LenLineEdit.text(),
                              "2", "3", self.recLenLineEdit.text()])
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
        self.pulse2LenLineEdit.setText(str(loaded_seq.p2))
        self.gapLenLineEdit.setText(str(loaded_seq.g1))
        self.recLenLineEdit.setText(str(loaded_seq.rec))
        # Set phase combo boxes
        set_combo_box(self.phaseComboBox, loaded_seq.TX_phase)

    def clear_seq_line_edits(self) -> None:
        """
        Clears all text-boxes on the 'Sequence' tab.
        :return:
        """
        # Clear all text boxes
        self.frequencyLineEdit.setText('')
        self.pulse1LenLineEdit.setText('')
        self.pulse2LenLineEdit.setText('')
        self.gapLenLineEdit.setText('')
        self.recLenLineEdit.setText('')
        self.savedSeqLineEdit.setText('')
        # Reset phase combo box
        self.phaseComboBox.setCurrentIndex(0)

    def update_experiment_treewidget(self) -> None:
        """
        Updates the Experiment TreeWidget to display all commands in the experiment manager.
        :return:
        """

        # Clear treewidget
        self.exptTreeWidget.clear()

        print(self.expt_manager.command_list)
        # Repopulate treewidget
        for com in self.expt_manager.command_list:
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
                self.expt_manager.add_command(command)
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

            self.expt_manager.add_command(new_command)
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
            baseNode = selected_item[0]
            # Get index of selected node
            index = self.exptTreeWidget.indexFromItem(baseNode).row()
            # Delete selected node
            self.expt_manager.delete_command(index)
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
        command_type = self.expt_manager.get_command_type(item_index)

        value = None
        rate = None
        value_valid = None
        rate_valid = None

        # If NMRCommand
        if command_type is NMRCommand:
            repeats, valid = QtWidgets.QInputDialog.getInt(self.dialog, 'Repeats', 'Enter number of repeats', 1, 1)
            if valid:
                self.expt_manager.edit_command(item_index, repeats=repeats)

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

        # Reset command count
        self.current_command = 0

        # Generate directory to hold output data files
        self.create_data_directory()

        # Check if command list is empty
        self.total_commands = self.exptTreeWidget.topLevelItemCount()

        # If TreeWidget is empty show error messagebox
        if self.total_commands == 0:
            msg_text = 'No commands selected in \'Experiment\' tab!'
            self.show_dialog(msg_text)
        else:
            # Run first command in the list
            self.run_command()
            # Disable start button
            self.startExptBtn.setDisabled(True)

    def run_command(self):

        def process_PPMS_command(com):

            if 'Temperature' in com:
                # Extract set value
                value_str = com.split('\n')[0]
                value = value_str.split(' ')[-1][:-2]

                # Extract rate
                rate_str = com.split('\n')[1]
                rate = rate_str.split(' ')[1][:-4]

                variable_type = 'T'

            else:
                # Extract set value
                value_str = command.split('\n')[0]
                value = value_str.split(' ')[-1][:-3]

                # Extract rate
                rate_str = command.split('\n')[1]
                rate = rate_str.split(' ')[1][:-5]
                # Define temp or field
                variable_type = 'F'

            return variable, value, rate

        def run_NMR_sequence(reg_vals, num_reps, data_filepath, seq_names):
            """
            Runs an NMR sequence in a separate thread.
            """
            # Create QThread object
            self.thread = QThread()
            # Create Worker instance for spectrometer
            self.worker = SpecMRWorker(self.spectrometer, reg_vals, num_reps, data_filepath, seq_names)
            # Move worker to thread
            self.worker.moveToThread(self.thread)
            # Connect signals and slots
            self.thread.started.connect(self.worker.run_expt)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.data_out.connect(self.plot_data)
            self.thread.destroyed.connect(self.run_command)
            self.worker.expt_info.connect(self.update_expt_labels)
            self.thread.finished.connect(self.thread.deleteLater)
            # Start thread
            self.thread.start()

        def run_PPMS_command(parameter, value, rate):
            """
            Runs a PPMS command in a separate thread.
            """

            # Create QThread object
            self.thread = QThread()
            # Create Worker instance for PPMS
            self.worker = PPMSWorker(parameter, value, rate)
            # Move worker to thread
            self.worker.moveToThread(self.thread)

            # Connect signals and slots
            self.thread.started.connect(self.worker.set_value)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.command_info.connect(self.update_expt_labels)
            self.worker.parameters.connect(self.update_live_PPMS_plot)
            self.thread.destroyed.connect(self.run_command)
            self.thread.finished.connect(self.thread.deleteLater)

            # Start thread
            self.thread.start()

        def change_item_colour(it, col):

            it.setForeground(0, col)
            it.setForeground(1, col)
            it.setForeground(2, col)


        print(f'Current command: {self.current_command}')

        # Change previous command to black
        if self.current_command != 0:
            prev_item = self.exptTreeWidget.topLevelItem(self.current_command-1)
            change_item_colour(prev_item, QBrush(QColor('#000000')))

        if self.current_command < self.total_commands:

            # Get current command
            item = self.exptTreeWidget.topLevelItem(self.current_command)
            # Change current command to green
            change_item_colour(item, QBrush(QColor('#00FF00')))
            # Get command type
            command_type = item.text(0)
            # Increment current command counter
            self.current_command += 1

            if self.spectrometer:
                # Check if command is NMR or PPMS
                if command_type == 'NMR':
                    # Get sequence name and repeats
                    seq_name = item.text(1)
                    repeats = item.text(2)

                    # Make output data file
                    self.create_data_file(seq_name, int(repeats))

                    # Generate output data filepaths
                    data_filepath = self.default_data_filepath + self.sample_name + '\\' + self.sample_name + '_' + seq_name

                    # Read sequence from file
                    sequence_vals = np.loadtxt(self.default_seq_filepath + seq_name + '.seq', dtype=int)
                    # Delete phase since it is not implemented yet
                    sequence_vals = np.delete(sequence_vals, 1)

                    # Construct tuples of (Register, value) pairs
                    register_values = np.empty(sequence_vals.size, dtype=object)
                    for j, t in enumerate(zip(self.registers, sequence_vals)):
                        register_values[j] = (t[0], t[1])

                    run_NMR_sequence(register_values, repeats, data_filepath, seq_name)

                else:
                    # Extract command
                    command = item.text(1)
                    # Process PPMS command
                    variable, value, rate = process_PPMS_command(command)
                    # Run command
                    run_PPMS_command(variable, value, rate)
            else:
                # Wait 2 seconds
                QtCore.QTimer.singleShot(2000, lambda: self.run_command())

        else:
            print('Main Thread: Experiment finished!')
            self.reset_expt_tab()

    def update_live_PPMS_plot(self, t, temp):
        print(f'{t}s')
        print(f'Temp = {temp}K')

        self.t_data.append(t)
        self.temp_data.append(temp)

        self.livePPMSPlotWidget.canvas.ax.plot(self.t_data, self.temp_data, 'r.-')
        self.livePPMSPlotWidget.canvas.draw()

    def select_live_sequence(self):
        # Open file dialog
        load_filepath = QtWidgets.QFileDialog.getOpenFileName(None, "Open sequence", self.default_seq_filepath)
        # Read file name of sequence
        load_filename = load_filepath[0].split('/')[-1]
        # Set loaded file textbox
        self.livePlotSelectedSeqLineEdit.setText(load_filename)

    def start_live_plot(self):
        """
        Starts live plotting.
        """

        if self.livePlotSelectedSeqLineEdit.text() == "":
            self.select_live_sequence()

        seq_path = self.default_seq_filepath + self.livePlotSelectedSeqLineEdit.text()
        data = np.loadtxt(seq_path)
        data = np.delete(data, 1)

        # Regs to update
        regs_to_update = np.array([1, 2, 3, 5, 7])
        reg_vals = np.empty(regs_to_update.size, dtype=tuple)

        for index, reg in enumerate(regs_to_update):
            pair = (reg, int(data[index]))
            reg_vals[index] = pair

        # Set fixed register values for now
        # reg_vals2 = np.array([(1, int(10e6)), (2, int(1e4)), (3, int(2e4)), (5, int(1e4)), (7, int(5e4))])

        # Setup new thread for continuous acquisition
        self.liveThread = QThread()
        self.liveWorker = SpecLiveWorker(self.spectrometer, reg_vals)
        self.liveWorker.moveToThread(self.liveThread)

        self.liveThread.started.connect(self.liveWorker.continuous_acquisition)
        self.liveThread.finished.connect(self.liveThread.deleteLater)

        self.liveWorker.data_out.connect(self.fetch_live_plot_data)
        self.liveWorker.finished.connect(self.liveThread.quit)
        self.liveWorker.finished.connect(self.liveWorker.deleteLater)

        # Start thread
        self.liveThread.start()

        # Disable live button
        self.startLivePlot.setEnabled(False)
        # Enable live button on thread finish
        self.liveThread.finished.connect(lambda: self.startLivePlot.setEnabled(True))

        # Start timer for plots
        self.update_timer.start(500)

    def end_live_plot(self):
        """
        Ends live plotting from SDR14.
        :return:
        """

        self.liveWorker.stop_acquisition()
        self.update_timer.stop()

    def fetch_live_plot_data(self, ch1_data, ch2_data):
        """
        :param ch1_data: Data from SDR14 ch1 emitted from worker thread.
        :param ch2_data: Data from SDR14 ch2 emitted from worker thread.
        :return:
        """

        # Assign data from SDR14 worker thread to class variables
        self.ch1_data = ch1_data
        self.ch2_data = ch2_data

        # Add to accumulator variable

    def update_live_plot_on_timeout(self):
        """
        Updates time and frequency live tab plots incoming data from SDR14 on QTimer timeout.
        """

        def plot_time_data(x, ch1_data, ch2_data):

            if (self.time_plot_line["Channel A"] is None) and (self.time_plot_line["Channel B"] is None):
                # If plots are blank, generate plot references
                plot_refs = self.liveTimePlotWidget.canvas.ax.plot(x, ch1_data, x, ch2_data)

                self.time_plot_line["Channel A"] = plot_refs[0]
                self.time_plot_line["Channel A"].set_label('CH A')

                self.time_plot_line["Channel B"] = plot_refs[1]
                self.time_plot_line["Channel B"].set_label('CH B')
                self.liveTimePlotWidget.canvas.ax.legend(loc='upper right')

            else:
                # Update plot references
                self.time_plot_line["Channel A"].set_ydata(ch1_data)
                self.time_plot_line["Channel B"].set_ydata(ch2_data)

            self.liveTimePlotWidget.canvas.draw()

        def plot_frq_data(xf, ch1_FFT, ch2_FFT):

            N = ch1_FFT.size
            ind = int(N/2)
            y1 = np.abs(ch1_FFT[0:ind:10])
            y2 = np.abs(ch2_FFT[0:ind:10])

            ind = int(N/2)

            if (self.frq_plot_line["Channel A"] is None) and (self.frq_plot_line["Channel B"] is None):

                x = xf[0:ind:10]
                # If plots are blank, generate plot references
                plot_refs = self.liveFrqPlotWidget.canvas.ax.plot(x, y1, x, y2)

                self.frq_plot_line["Channel A"] = plot_refs[0]
                self.frq_plot_line["Channel A"].set_label('CH A')

                self.frq_plot_line["Channel B"] = plot_refs[1]
                self.frq_plot_line["Channel B"].set_label('CH B')
                self.liveFrqPlotWidget.canvas.ax.legend(loc='upper right')
            else:
                # Update plot references
                self.frq_plot_line["Channel A"].set_ydata(y1)
                self.frq_plot_line["Channel B"].set_ydata(y2)

            self.liveFrqPlotWidget.canvas.draw()

        def fourier_transform(data, fs):
            Ts = 1 / fs
            N = data.size
            data_FFT = scipy.fft.fft(data)
            xf = scipy.fft.fftfreq(N, d=Ts)

            return xf, data_FFT

        N = 1000
        x = np.arange(0, N)

        # Plot time data
        plot_time_data(x, self.ch1_data[0:N], self.ch2_data[0:N])
        # Calculate FFT of incoming data
        ch1_xf, ch1_FFT = fourier_transform(self.ch1_data, fs=800e6)
        ch2_xf, ch2_FFT = fourier_transform(self.ch2_data, fs=800e6)
        # Plot frq data
        plot_frq_data(ch1_xf, ch1_FFT, ch2_FFT)

    def reset_expt_tab(self):
        """
        Resets the 'Experiment' tab layout after an experiment is finished.
        """

        self.startExptBtn.setDisabled(False)

    def update_expt_labels(self, seq_name, repeat='--'):
        """
        Updates the 'Experiment' tab labels during the experiment.
        """
        #self.currentSeqLbl.setText('Current Sequence: {seq_name}'.format(seq_name))
        self.currentRepeatLbl.setText(f'Current Repeat: {repeat}')

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
