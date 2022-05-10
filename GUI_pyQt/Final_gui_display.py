from gui_8 import *
import sys

class RunApp(Ui_MainWindow):

    def __init__(self, window):

        # Setup GUI components
        self.setupUi(window)




app = QtWidgets.QApplication(sys.argv)
# Handle application close
MainWindow = QtWidgets.QMainWindow()
ui = RunApp(MainWindow)
MainWindow.show()
app.exec_()