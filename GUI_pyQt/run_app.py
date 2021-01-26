from gui_2 import *
import sys
import numpy as np

class RunApp(Ui_mainWindow):

    def __init__(self, window):

        self.setupUi(window)
        self.dataFileGenerateLbl.setHidden(True)
        self.mainTab.setCurrentIndex(0)

        self.clearAllBtn.clicked.connect(self.clear_txt)
        self.loadSeqBtn.clicked.connect(self.load_seq_file)
        self.saveSeqBtn.clicked.connect(self.save_seq_file)
        self.sampleTabNextBtn.clicked.connect(self.next_tab)
        self.seqTabNextBtn.clicked.connect(self.next_tab)
        self.seqTabReturnBtn.clicked.connect(self.prev_tab)
        self.genDataFileBtn.clicked.connect(self.gen_data_file)
        self.addSeqBtn.clicked.connect(self.add_seq_to_chain)
        self.removeSeqBtn.clicked.connect(self.remove_seq_from_chain)

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
        load_filepath = QtWidgets.QFileDialog.getOpenFileName()
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

    def gen_data_file(self):

        sample_name = self.sampleNameLineEdit.text()
        sample_mass = self.sampleMassLineEdit.text()
        data_filepath = QtWidgets.QFileDialog.getSaveFileName()
        self.SaveFileLocLineEdit.setText(data_filepath[0])
        # Write header
        f = open(data_filepath[0], "w+")
        f.write("[HEADER]\n")
        f.write("SAMPLE NAME, {}\n".format(sample_name))
        f.write("SAMPLE MASS (mg), {}\n".format(sample_mass))
        f.write("[Data]\n")
        f.close()
        self.dataFileGenerateLbl.setHidden(False)

    def add_seq_to_chain(self):
        # Open file dialog
        load_filepath = QtWidgets.QFileDialog.getOpenFileName()
        # Read file name of sequence
        load_filename = load_filepath[0].split('/')[-1]
        # Add data to tree widget [FILEPATH, REPEATS] (repeats = 1 by default)
        item = QtWidgets.QTreeWidgetItem(self.chainTreeWidget, [load_filename, '1'])
        self.chainTreeWidget.addTopLevelItem(item)

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


app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = RunApp(MainWindow)
MainWindow.show()
app.exec_()