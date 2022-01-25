from PPMS_command_window import *
import sys
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal

class runPPMSCommandWindow(Ui_PPMSCommandWindow, QObject):

    submitted = pyqtSignal(str, str, str)

    def __init__(self, window):

        # Setup GUI components
        super().__init__()
        self.setupUi(window)

        # Connect functions to buttons
        self.acceptBtn.clicked.connect(self.accept_values)
        self.returnBtn.clicked.connect(self.close_window)

    def accept_values(self):
        # Temp = 0, Field = 1
        parameter = self.parameterComboBox.currentIndex()

        # Check if value is a float
        try:
            value = float(self.valLineEdit.text())
        except:
            value = 1e6

        # Check if rate is a float
        try:
            rate = float(self.lineEdit.text())
        except:
            rate = 0

        valid = 0
        # Check temperature and field values are valid
        # T range: 2K - 400K, rate: 2K/s - 20K/s
        if parameter == 0:
            if (2 <= value <= 400) and (2 <= rate <= 20):
                valid = 1
        else:
            # Field range = -70,000Oe - 70,000Oe
            if -70000 <= value <= 70000 and (1 <= rate <= 500):
                valid = 1

        if valid:
            # Send to main window
            self.submitted.emit(str(parameter), str(value), str(rate))
        else:
            # Show error message
            if parameter == 0:
                self.show_dialog('Invalid value or rate.\n'
                                 'Temperature value must be between 2K and 400K.\n'
                                 'Temperature rate must be between 2K/s and 20K/s.')
            else:
                self.show_dialog('Invalid value or rate.\n'
                                 'Field value must be between -70,000Oe - 70,000Oe.\n'
                                 'Field rate must be between 1Oe/s and 500Oe/s.')

    def close_window(self):
        print('#')
        pass

    def show_dialog(self, msg_text):
        """
        Convenience function to show a warning dialog with custom text.

        """

        msgbox = QtWidgets.QMessageBox()
        msgbox.setText(msg_text)
        msgbox.setWindowTitle("Warning")
        msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgbox.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = runPPMSCommandWindow(MainWindow)
    MainWindow.show()
    app.exec_()
