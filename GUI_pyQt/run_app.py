from gui_2 import *
import sys
import numpy as np
import time
import os

import ADQ_tools_lite

class RunApp(Ui_mainWindow):

    def __init__(self, window):

        self.setupUi(window)
        self.dialog = QtWidgets.QInputDialog()

        # Can this stuff be changed in qtdesigner?
        self.dataFileGenerateLbl.setHidden(True)
        self.mainTab.setCurrentIndex(0)
        self.textEdit.setReadOnly(True)
        self.font = QtGui.QFont()
        self.font.setPointSize(12)
        self.textEdit.setFont(self.font)


        self.clearAllBtn.clicked.connect(self.clear_txt)
        self.loadSeqBtn.clicked.connect(self.load_seq_file)
        self.saveSeqBtn.clicked.connect(self.save_seq_file)
        self.sampleTabNextBtn.clicked.connect(self.next_tab)
        self.seqTabNextBtn.clicked.connect(self.next_tab)
        self.seqTabReturnBtn.clicked.connect(self.prev_tab)
        self.genDataFileBtn.clicked.connect(self.get_sample_info)
        self.addSeqBtn.clicked.connect(self.add_seq_to_chain)
        self.removeSeqBtn.clicked.connect(self.remove_seq_from_chain)
        self.chainTreeWidget.itemDoubleClicked.connect(self.display_seq)
        self.function1Btn.clicked.connect(self.run_seq)
        self.function2Btn.clicked.connect(self.create_data_directory)

        try:
            self.device = ADQ_tools_lite.sdr14()
        except IOError:
            self.device = None
            print('No device connected!')


        # Initialise default sequence and data filepaths
        self.default_seq_filepath = 'sequences\\'
        self.default_data_filepath = 'data\\'

        # Initialise sample parameters
        self.sample_name = ''
        self.sample_mass = 0.0

        self.num_parameters = 6

    def clear_txt(self):
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
        current_index = self.mainTab.currentIndex()
        next_index = current_index + 1
        self.mainTab.setCurrentIndex(next_index)

    def prev_tab(self):
        current_index = self.mainTab.currentIndex()
        prev_index = current_index - 1
        self.mainTab.setCurrentIndex(prev_index)

    def get_sample_info(self):

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
            self.sample_name = name
            self.sample_mass = float(mass)

    def add_seq_to_chain(self):
        # Open file dialog
        load_filepath = QtWidgets.QFileDialog.getOpenFileName(None, "Open sequence", self.default_seq_filepath)
        # Read file name of sequence
        load_filename = load_filepath[0].split('/')[-1]
        # Get number of repeats
        repeats, valid = QtWidgets.QInputDialog.getInt(self.dialog, 'Repeats', 'Enter number of repeats')

        # Add data to tree widget [FILEPATH, REPEATS] (repeats = 1 by default)
        if valid and repeats > 0:
            item = QtWidgets.QTreeWidgetItem(self.chainTreeWidget, [load_filename, str(repeats)])
            self.chainTreeWidget.addTopLevelItem(item)
        else:
            self.show_dialog('Invalid entry!')

    def remove_seq_from_chain(self):
        # Check for selected items
        selected_item = self.chainTreeWidget.selectedItems()
        # If an item is selected
        if selected_item:
            # Get selected node
            baseNode = selected_item[0]
            # Get index of selected node
            index = self.chainTreeWidget.indexFromItem(baseNode)
            # Delete selected node
            self.chainTreeWidget.takeTopLevelItem(index.row())
            self.textEdit.clear()

    def display_seq(self, selected_item, col):

        print(col)

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
                self.textEdit.clear()

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

                self.textEdit.setHtml(seq_text)
            except:
                print('Error!')

        elif col == 1:
            print('Sequence number clicked')

    def run_seq(self):

        # Generate directory to hold output data files
        self.create_data_directory()

        # Get number of sequences in TreeWidget
        num_seq = self.chainTreeWidget.topLevelItemCount()

        # If TreeWidget is empty show error messagebox
        if num_seq == 0:
            msg_text = 'No sequences selected in \'chain\' tab!'
            self.show_dialog(msg_text)
        else:
            # Get sequence names and number of repeats from TreeWidget
            seq_filenames = np.empty(num_seq, dtype=object)
            num_reps = np.empty(num_seq)

            for i in range(num_seq):
                # Get each item in TreeWidget
                item = self.chainTreeWidget.topLevelItem(i)
                seq_name = item.text(0)
                repeats = item.text(1)

                # Generate data file for each sequence
                self.create_data_file(seq_name[:-4], int(repeats))

                # Add filenames to array
                seq_filenames[i] = self.default_seq_filepath + seq_name
                # Add number of repeats to array
                num_reps[i] = int(repeats)


       
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



            for i in range(num_seq):
                # Get reg values and number of repeats for sequence i
                reg = reg_vals[:, i]
                reps = num_reps[i]
                # Initialise k
                k = 0
                # Loop for number of repeats
                while k < reps:
                     # Write reg values to device
                    for j in reg:
                        self.device.reg_write(*j)
                    # Enable device
                    self.device.enable_dev()
                    print('Device enabled with register vales: ' + str(reg))
                    print('Experiment number: {}'.format(k+1))
                    time.sleep(10)
                    # Disable device
                    self.device.disable_dev()
                    print('Device disabled')
                    time.sleep(5)
                    # Increment k
                    k += 1
            print('Experiments finished!')


    def create_data_directory(self):

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

        # Initialise loop variable
        i = 0

        # Repeat for number of repeats
        while i < rep:
            # Construct file path (data/sample name/sample name + seq name + expt number.txt)
            file_path = self.default_data_filepath + self.sample_name + '\\' + self.sample_name + '_' + seq_name + '_expt{}'.format(i+1) +'.txt'
            print(file_path)

            # Create data file
            f = open(file_path, "w+")

            # Write header
            f.write("[HEADER]\n")
            f.write("SAMPLE NAME, {}\n".format(self.sample_name))
            f.write("SAMPLE MASS (mg), {}\n".format(self.sample_mass))
            f.write("SEQUENCE, {}\n".format(seq_name))
            f.write("EXPERIMENT NUMBER, {}\n".format(i+1))
            f.write("[Data]\n")
            f.close()

            i += 1

    def show_dialog(self, msg_text):

        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg_text)
        msgbox.setWindowTitle("Warning")
        msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgbox.exec()

app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = RunApp(MainWindow)
MainWindow.show()
app.exec_()