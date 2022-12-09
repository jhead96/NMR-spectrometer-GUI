from PPMS_command_window import *
import sys
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal


class runPPMSCommandWindow(Ui_PPMSCommandWindow, QObject):

    PPMS_parameters = pyqtSignal(str, float, float)

    def __init__(self, window) -> None:

        # Setup GUI components
        super().__init__()
        self.setupUi(window)

        # Setup variables
        self.parameter = None
        self.value = None
        self.rate = None

        # Connect functions to buttons
        self.acceptBtn.clicked.connect(self.input_values)
        self.returnBtn.clicked.connect(self.close_window)

    def set_variables(self, parameter: str, value: float, rate: float) -> None:
        self.parameter = parameter
        self.value = value
        self.rate = rate

    def emit_parameters(self) -> None:
        self.PPMS_parameters.emit(self.parameter, self.value, self.rate)

    def input_values(self) -> None:
        # Temp = 0, Field = 1
        parameter = self.parameterComboBox.currentIndex()

        # Check type
        try:
            value = float(self.valLineEdit.text())
            rate = float(self.lineEdit.text())
        except ValueError as ex:
            print(ex)
            self.show_dialog("Invalid type for set value or rate!")
            return

        # Check temperature and field values are valid
        # T range: 2K - 400K, rate: 2K/s - 20K/s
        if parameter == 0:
            if (2 <= value <= 400) and (2 <= rate <= 20):
                self.set_variables("Temperature", value, rate)
                self.emit_parameters()
            else:
                self.show_dialog('Invalid value or rate.\n'
                                 'Temperature value must be between 2K and 400K.\n'
                                 'Temperature rate must be between 2K/s and 20K/s.')

        else:
            # Field range = -70,000Oe - 70,000Oe
            if (-70000 <= value <= 70000) and (10 <= rate <= 500):
                self.set_variables("Field", value, rate)
                self.emit_parameters()
            else:
                self.show_dialog('Invalid value or rate.\n'
                                 'Field value must be between -70,000 Oe and 70,000 Oe.\n'
                                 'Field rate must be between 1O Oe/s and 500 Oe/s.')

    def close_window(self) -> None:
        print('#')
        pass

    def show_dialog(self, msg_text: str) -> None:
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
