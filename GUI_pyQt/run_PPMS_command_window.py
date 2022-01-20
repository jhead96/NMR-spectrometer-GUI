from PPMS_command_window import *
import sys
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal

class runPPMSCommandWindow(Ui_PPMSCommandWindow, QObject):

    submitted = pyqtSignal(str, str)

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
            self.show_dialog('Invalid value!')
            value = 1e6

        valid = 0
        # Check temperature and field values are valid
        # T range: 2K - 400K
        if parameter == 0:
            if 2 <= value <= 400:
                valid = 1
        else:
            # Field range = -70,000Oe - 70,000Oe
            if -70000 <= value <= 70000:
                valid = 1

        if valid:
            # Send to main window
            self.submitted.emit(str(parameter), str(value))
            #print('Data sent!')
        else:
            # Show error message
            if parameter == 0:
                self.show_dialog('Invalid value. Temperature value must be between 2K - 400K')
            else:
                self.show_dialog('Invalid value. Field value must be between -70,000Oe - 70,000Oe')



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
