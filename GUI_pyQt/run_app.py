from gui_6 import *
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy
import time
import os
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal

import ADQ_tools_lite

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

    def __init__(self, device, reg_vals, num_reps, data_filepaths, seq_names):
        super().__init__()
        self.device = device
        self.reg_vals = reg_vals
        self.num_reps = num_reps
        self.num_seqs = np.size(num_reps)
        self.data_filepaths = data_filepaths
        self.seq_names = seq_names


    def run_expt(self):
        """
        Runs an experiment on the SDR14 using the parameters entered on the 'Experiment' tab of the GUI.
        Saves 1 record of data from the SDR14 using the MultiRecord mode to a text file.
        """

        for i in range(self.num_seqs):
            # Get reg values and number of repeats for sequence i
            reg = self.reg_vals[:, i]
            reps = self.num_reps[i]
            # Initialise k
            k = 0
            # Loop for number of repeats
            while k < reps:
                # Write reg values to device
                for j in reg:
                    self.device.reg_write(*j)

                # Emit expt info
                self.expt_info.emit(self.seq_names[i], k + 1)

                # Enable device
                self.device.enable_dev()

                # Start MR acquisition
                ch1_data, ch2_data = self.device.MR_acquisition()
                # Save to file
                self.save_data_to_file(self.data_filepaths[i, k], ch1_data, ch2_data)

                print('Sequence name: {}'.format(self.seq_names[i]))
                print('Experiment number: {}'.format(k + 1))
                print('Data file path: {}'.format(self.data_filepaths[i, k]))

                time.sleep(5)

                # Disable device
                self.device.disable_dev()
                print('Device disabled')
                time.sleep(5)
                self.clear_console()
                # Increment k
                k += 1

        print('Experiment finished!')

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

    def clear_console(self):
        """
        Function that clears the Python console.
        """
        clear = "\n" * 100
        print(clear)

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

class RunApp(Ui_mainWindow):
    """
    Class to handle operation of the GUI on the main thread.
    """

    def __init__(self, window):

        # Setup GUI components
        self.setupUi(window)
        self.dialog = QtWidgets.QInputDialog()

        # Setup graph widgets
        self.initialise_plot_widgets()
        self.live_time_plot_ref = {"Channel A": None, "Channel B": None}
        self.live_frq_plot_ref = {"Channel A": None, "Channel B": None}

        # Setup live plotting timer and data variables
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_live_plot_on_timeout)
        self.ch1_data = None
        self.ch2_data = None

        # Can this stuff be changed in qtdesigner?
        self.mainTab.setCurrentIndex(0)
        self.exptTextEdit.setReadOnly(True)
        self.font = QtGui.QFont()
        self.font.setPointSize(12)
        self.exptTextEdit.setFont(self.font)

        # Connect buttons to functions
        # Sample tab
        self.confirmSampleInfoBtn.clicked.connect(self.get_sample_info)
        self.sampleTabNextBtn.clicked.connect(self.next_tab)
        self.clearSampleInfoBtn.clicked.connect(self.clear_sample_info)

        # Sequence tab
        self.clearAllBtn.clicked.connect(self.clear_txt)
        self.loadSeqBtn.clicked.connect(self.load_seq_file)
        self.saveSeqBtn.clicked.connect(self.save_seq_file)
        self.seqTabNextBtn.clicked.connect(self.next_tab)
        self.seqTabReturnBtn.clicked.connect(self.prev_tab)

        # Experiment tab
        self.addSeqBtn.clicked.connect(self.add_spec_command)
        self.removeSeqBtn.clicked.connect(self.remove_command)
        self.editSeqBtn.clicked.connect(self.edit_seq)
        self.exptTreeWidget.itemDoubleClicked.connect(self.display_command)

        # Run tab
        self.runExptBtn.clicked.connect(self.run_expt)

        # Data tab
        self.browseDataFolderBtn.clicked.connect(self.get_data_directory)
        self.updatePlotBtn.clicked.connect(self.plot_data)

        # Live tab
        self.startLivePlot.clicked.connect(self.start_live_plot)
        self.endLivePlot.clicked.connect(self.end_live_plot)
        # CHANGE IN QTDESIGNER
        self.pushButton.clicked.connect(self.select_live_sequence)

        # Check for SDR14 connection
        try:
            self.device = ADQ_tools_lite.sdr14()
        except IOError:
            self.device = None
            print('No device connected!')

        # Initialise default sequence and data filepaths
        self.default_seq_filepath = 'sequences\\'
        self.default_data_filepath = 'data\\'

        # Initialise data file cache
        self.data_file_cache = []
        # Initialise sample parameters
        self.sample_name = ''
        self.sample_mass = 0.0

        self.num_parameters = 6

    def initialise_plot_widgets(self):
        self.liveTimePlotWidget.canvas.ax.set_title('Signal from SDR14')
        self.liveTimePlotWidget.canvas.ax.set_xlabel('Sample number')
        self.liveTimePlotWidget.canvas.ax.set_ylabel('Signal')

        self.liveFrqPlotWidget.canvas.ax.set_title('FFT of SDR14 signal')
        self.liveFrqPlotWidget.canvas.ax.set_xlabel('f (Hz)')
        self.liveFrqPlotWidget.canvas.ax.set_ylabel('Intensity (arb units)')

    def clear_txt(self):
        """
        Clears all text-boxes on the 'Sequence' tab.
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

    def load_seq_file(self):
        """
        Loads values from the designated sequence file into the 'Sequence' tab for editing.
        """
        # Open file dialog
        load_filepath = QtWidgets.QFileDialog.getOpenFileName(None, "Open sequence", self.default_seq_filepath)
        # Read file name of sequence
        load_filename = load_filepath[0].split('/')[-1]
        # Set loaded file textbox
        self.loadedSeqLineEdit.setText(load_filename)
        # Load data
        seq_data = np.loadtxt(load_filepath[0])
        # Move values from file into text-boxes
        self.frequencyLineEdit.setText(seq_data[0].astype(str))
        self.pulse1LenLineEdit.setText(seq_data[2].astype(str))
        self.pulse2LenLineEdit.setText(seq_data[3].astype(str))
        self.gapLenLineEdit.setText(seq_data[4].astype(str))
        self.recLenLineEdit.setText(seq_data[5].astype(str))
        # Set phase combo box
        if seq_data[1].astype(int) == 0:
            self.phaseComboBox.setCurrentIndex(0)
        elif seq_data[1].astype(int) == 90:
            self.phaseComboBox.setCurrentIndex(1)
        elif seq_data[1].astype(int) == 180:
            self.phaseComboBox.setCurrentIndex(2)
        elif seq_data[1].astype(int) == 270:
            self.phaseComboBox.setCurrentIndex(3)

    # noinspection PyTypeChecker
    def save_seq_file(self):
        """
        Saves sequence values from the 'Sequence' tab into a .seq file.
        """
        # Get save data filepath using windows dialog
        save_file_name = QtWidgets.QFileDialog.getSaveFileName(filter="seq files (*.seq)")
        # Combine data from text-boxes into array
        save_data = np.array([self.frequencyLineEdit.text(), self.phaseComboBox.currentText(),
                              self.pulse1LenLineEdit.text(), self.pulse2LenLineEdit.text(),
                              self.gapLenLineEdit.text(), self.recLenLineEdit.text()])
        # Convert to float
        save_data_float = save_data.astype(np.float)
        # Save data
        np.savetxt(save_file_name[0], save_data_float)
        # Update saved file text-box
        self.savedSeqLineEdit.setText(save_file_name[0])

    def next_tab(self):
        """
        Switches view the next tab in the GUI.
        """
        current_index = self.mainTab.currentIndex()
        next_index = current_index + 1
        self.mainTab.setCurrentIndex(next_index)

    def prev_tab(self):
        """
        Switches view to the previous tab in the GUI
        """
        current_index = self.mainTab.currentIndex()
        prev_index = current_index - 1
        self.mainTab.setCurrentIndex(prev_index)

    def get_sample_info(self):
        """
        Stores the sample information from the 'Sample' tab into the class.
        """

        def is_float(value):
            try:
                float(value)
                return True
            except ValueError:
                return False

        # Initialise valid flags
        name_valid = True
        mass_valid = True

        # Read sample information from text-boxes
        name = self.sampleNameLineEdit.text()
        mass = self.sampleMassLineEdit.text()

        # Check input sample name is valid
        if name == '':
            self.show_dialog('Invalid sample name!')
            name_valid = False
        # Check input sample mass is valid
        if not is_float(mass):
            self.show_dialog('Invalid sample mass!')
            mass_valid = False

        # If inputs are valid update variables
        if name_valid and mass_valid:
            # Update internal sample variables
            self.sample_name = name
            self.sample_mass = float(mass)

            # Update labels
            self.currentSampleNameLbl.setText('Current sample name: {}'.format(self.sample_name))
            self.currentSampleMassLbl.setText('Current sample mass: {} mg'.format(self.sample_mass))

    def clear_sample_info(self):
        """
        Clears sample info from the class.
        """
        # Reset internal sample variables
        self.sample_name = ""
        self.sample_mass = 0.0
        # Reset labels
        self.currentSampleNameLbl.setText('Current sample name: No sample entered!')
        self.currentSampleMassLbl.setText('Current sample mass: No sample entered!')
        # Clear textboxes
        self.sampleNameLineEdit.setText("")
        self.sampleMassLineEdit.setText("")

    def add_spec_command(self):
        """
        Allows a .seq file to be selected from a file dialog and added to the experiment tree widget.
        """
        # Open file dialog
        load_filepath = QtWidgets.QFileDialog.getOpenFileName(None, "Open sequence", self.default_seq_filepath)
        # Read file name of sequence
        load_filename = load_filepath[0].split('/')[-1][:-4]
        # Get number of repeats
        repeats, valid = QtWidgets.QInputDialog.getInt(self.dialog, 'Repeats', 'Enter number of repeats', 1, 1 )

        # Add data to tree widget [TYPE,  SEQ NAME, REPEATS]
        if valid and repeats > 0:
            item = QtWidgets.QTreeWidgetItem(self.exptTreeWidget, ['NMR', load_filename, str(repeats)])
            self.exptTreeWidget.addTopLevelItem(item)
        else:
            self.show_dialog('Invalid entry!')

    def remove_command(self):
        """
        Removes the selected sequence from the Experiment tree widget
        """
        # Check for selected items
        selected_item = self.exptTreeWidget.selectedItems()
        # If an item is selected
        if selected_item:
            # Get selected node
            baseNode = selected_item[0]
            # Get index of selected node
            index = self.exptTreeWidget.indexFromItem(baseNode)
            # Delete selected node
            self.exptTreeWidget.takeTopLevelItem(index.row())
            self.exptTextEdit.clear()

    def edit_seq(self):
        """
        Allows the user to edit the number of repeats for the selected sequence in the Experiment tree widget.

        """
        # Check for selected items
        selected_item = self.exptTreeWidget.selectedItems()

        # If an item is selected
        if selected_item:
            # Get node from tree
            node = selected_item[0]
            # Get new value for repeats
            repeats, valid = QtWidgets.QInputDialog.getInt(self.dialog, 'Repeats', 'Enter number of repeats')

            if valid and repeats > 0:
                # Write to tree
                node.setText(1,'{}'.format(repeats))

    def display_command(self, selected_item, col):
        """
        Displays the parameters in the selected sequence in the text box.
        """

        if col == 0:
            # Read name from QTreeWidget
            name = selected_item.text(col)

            # Replace try with check for file existing!
            try:
                # Construct full filepath
                seq_path = self.default_seq_filepath + name
                # Load sequence data
                seq_data = np.loadtxt(seq_path)
                # Clear textEdit
                self.exptTextEdit.clear()

                seq_text = 'Sequence data for ' + name + ' </br><style>table, td{{border: 1px solid black;' \
                                                            'border-collapse: collapse;text-align:center}}</style><table>' \
                                                            '<tr><th>Parameter</th><th>Value</th></tr>' \
                                                            '<tr><td>Frequency (MHz)</td><td>{}</td></tr>' \
                                                            '<tr><td>Phase</td><td>{}</td></tr>' \
                                                            '<tr><td>Pulse 1 length (ns)</td><td>{}</td></tr>' \
                                                            '<tr><td>Pulse 2 length (ns)</td><td>{}</td></tr>' \
                                                            '<tr><td>Gap length (ns)</td><td>{}</td></tr>' \
                                                            '<tr><td>Record length (ns)</td><td>{}</td></tr>' \
                                                            '</table>'.format(seq_data[0], seq_data[1],
                                                                              seq_data[2], seq_data[3],
                                                                              seq_data[4], seq_data[5])

                self.exptTextEdit.setHtml(seq_text)
            except:
                print('Error!')

        elif col == 1:
            print('Sequence number clicked')

    def run_expt(self):
        """
        Runs an experiment from the GUI. Output data files are generated with a header containing useful information.
        The sequences in the Experiment tree are parsed. An instance of the Worker class is generated to run the
        experiment on a secondary thread to keep the GUI responsive.
        """
        # Generate directory to hold output data files
        self.create_data_directory()

        # Parse TreeWidget ----------------------------------------------------------------------

        # Get number of sequences in TreeWidget
        num_seq = self.exptTreeWidget.topLevelItemCount()

        # If TreeWidget is empty show error messagebox
        if num_seq == 0:
            msg_text = 'No sequences selected in \'Experiment\' tab!'
            self.show_dialog(msg_text)
        else:
            # Get sequence names and number of repeats from TreeWidget
            seq_filenames = np.empty(num_seq, dtype=object)
            seq_names = np.empty(num_seq, dtype=object)
            seq_name_short = np.empty(num_seq, dtype=object)
            num_reps = np.empty(num_seq)

            for i in range(num_seq):
                # Get each item in TreeWidget
                item = self.exptTreeWidget.topLevelItem(i)
                seq_name = item.text(0)
                repeats = item.text(1)

                # Generate data file for each sequence
                self.create_data_file(seq_name[:-4], int(repeats))

                # Add filenames to array
                seq_name_short[i] = seq_name.split('.')[0]
                seq_names[i] = seq_name
                seq_filenames[i] = self.default_seq_filepath + seq_name

                # Add number of repeats to array
                num_reps[i] = int(repeats)

            # Reformat data filenames   ----------------------------------------------------------------
            # Get max reps
            max_reps = int(np.max(num_reps))
            # Generate empty filename array of correct shape
            self.data_file_cache = np.empty((num_seq, max_reps), dtype=object)

            # Populate array with filenames
            for i in range(num_seq):
                # Initialise loop variable
                k = 0
                while k < num_reps[i]:
                    filepath = self.default_data_filepath + self.sample_name + '\\' + self.sample_name + '_' + seq_name_short[i] + '_expt{}'.format(k+1) +'.txt'
                    print(filepath)
                    # Add to cache
                    self.data_file_cache[i, k] = filepath
                    # Increment
                    k += 1

            # Reformat data from .seq files ----------------------------------------------------------------

            # Read data from files
            parameter_values = np.zeros(self.num_parameters)

            for seq_name in seq_filenames:
                data = np.loadtxt(seq_name)
                parameter_values = np.vstack((parameter_values, data))

            # Delete first row of array
            parameter_values = np.delete(parameter_values, 0, axis=0)

            # Delete phase for debugging purposes
            parameter_values = np.delete(parameter_values, 1, axis=1)

            # Construct 2D array of reg tuples - (reg_number, value)
            regs_to_update = np.array([1, 2, 3, 5, 7])
            reg_vals = np.empty((regs_to_update.size, num_seq), dtype=tuple)
            for i in range(regs_to_update.size):
                for j in range(num_seq):
                    # Generate
                    pair = (regs_to_update[i], int(parameter_values[j, i]))
                    reg_vals[i, j] = pair

            # Multi threading code to run experiment --------------------------------------------------------

            # Create QThread object
            self.thread = QThread()
            # Create Worker instance
            self.worker = SpecMRWorker(self.device, reg_vals, num_reps, self.data_file_cache, seq_name_short)
            # Move worker to thread
            self.worker.moveToThread(self.thread)
            # Connect signals and slots
            self.thread.started.connect(self.worker.run_expt)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.data_out.connect(self.plot_data)
            self.worker.expt_info.connect(self.update_expt_labels)
            self.thread.finished.connect(self.thread.deleteLater)
            # Start thread
            self.thread.start()

            # Disable run experiment button
            self.runExptBtn.setEnabled(False)
            # On thread finished reset experiment tab
            self.thread.finished.connect(self.reset_expt_tab)

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
        self.liveWorker = SpecLiveWorker(self.device, reg_vals)
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

            if (self.live_time_plot_ref["Channel A"] is None) and (self.live_time_plot_ref["Channel B"] is None):
                # If plots are blank, generate plot references
                plot_refs = self.liveTimePlotWidget.canvas.ax.plot(x, ch1_data, x, ch2_data)

                self.live_time_plot_ref["Channel A"] = plot_refs[0]
                self.live_time_plot_ref["Channel A"].set_label('CH A')

                self.live_time_plot_ref["Channel B"] = plot_refs[1]
                self.live_time_plot_ref["Channel B"].set_label('CH B')
                self.liveTimePlotWidget.canvas.ax.legend(loc='upper right')

            else:
                # Update plot references
                self.live_time_plot_ref["Channel A"].set_ydata(ch1_data)
                self.live_time_plot_ref["Channel B"].set_ydata(ch2_data)

            self.liveTimePlotWidget.canvas.draw()

        def plot_frq_data(xf, ch1_FFT, ch2_FFT):

            N = ch1_FFT.size
            ind = int(N/2)
            y1 = np.abs(ch1_FFT[0:ind:10])
            y2 = np.abs(ch2_FFT[0:ind:10])

            ind = int(N/2)

            if (self.live_frq_plot_ref["Channel A"] is None) and (self.live_frq_plot_ref["Channel B"] is None):

                x = xf[0:ind:10]
                # If plots are blank, generate plot references
                plot_refs = self.liveFrqPlotWidget.canvas.ax.plot(x, y1, x, y2)

                self.live_frq_plot_ref["Channel A"] = plot_refs[0]
                self.live_frq_plot_ref["Channel A"].set_label('CH A')

                self.live_frq_plot_ref["Channel B"] = plot_refs[1]
                self.live_frq_plot_ref["Channel B"].set_label('CH B')
                self.liveFrqPlotWidget.canvas.ax.legend(loc='upper right')
            else:
                # Update plot references
                self.live_frq_plot_ref["Channel A"].set_ydata(y1)
                self.live_frq_plot_ref["Channel B"].set_ydata(y2)

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
        self.runExptBtn.setEnabled(True)
        self.currentSeqLbl.setText('Current Sequence: ')
        self.currentRepeatLbl.setText('Current Repeat: ')

    def update_expt_labels(self, seq_name, repeat):
        """
        Updates the 'Experiment' tab labels during the experiment.
        """
        self.currentSeqLbl.setText('Current Sequence: {}'.format(seq_name))
        self.currentRepeatLbl.setText('Current Repeat: {}'.format(repeat))

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
            f.write("SAMPLE NAME, {}\n".format(self.sample_name))
            f.write("SAMPLE MASS (mg), {}\n".format(self.sample_mass))
            f.write("SEQUENCE, {}\n".format(seq_name))
            f.write("EXPERIMENT NUMBER, {}\n".format(i+1))
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

    def show_dialog(self, msg_text):
        """
        Convenience function to show a warning dialog with custom text.

        """

        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg_text)
        msgbox.setWindowTitle("Warning")
        msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgbox.exec()

def close_GUI():
    """
    Disconnects devices from the PC as the GUI is closed.
    """
    # Remove connection to SDR-14 if connected
    if ui.device:
        ui.device.delete_cu()

app = QtWidgets.QApplication(sys.argv)
# Handle application close
app.aboutToQuit.connect(close_GUI)
MainWindow = QtWidgets.QMainWindow()
ui = RunApp(MainWindow)
MainWindow.show()
app.exec_()