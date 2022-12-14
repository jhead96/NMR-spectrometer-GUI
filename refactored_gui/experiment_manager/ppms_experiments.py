from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal

class PPMSWorker(QObject):
    # Finished signal
    finished = pyqtSignal()
    # Command info signal
    command_info = pyqtSignal(object)
    # Parameters signal
    parameters = pyqtSignal(float, float)

    def __init__(self, device, command):
        super().__init__()
        self.device = device
        self.command = command

    def extract_parameters(self) -> None:
        pass

    def test_method(self):
        print(f"PPMS thread created with:\n"
              f"device = {self.device}\n"
              f"command = {self.command}\n")
        self.finished.emit()
