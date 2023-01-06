from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from refactored_gui.instrument_controllers.sdr14_controller import SDR14
from refactored_gui.instrument_controllers.ppms_controller import PPMS
import time
import numpy as np


class SpectrometerController(QObject):

    finished = pyqtSignal()
    current_repeat = pyqtSignal(int)
    data_out = pyqtSignal(object, object)

    def __init__(self) -> None:
        super().__init__()
        self.spectrometer = SDR14()
        print("[NMR Thread] __init__()")

    @pyqtSlot(object)
    def run_command(self, command) -> None:
        self.prepare_device(command.sequence)
        repeats = command.repeats
        print(f"[NMR Thread] Running dummy code with command = {command}")
        for i in range(0, repeats):
            self.current_repeat.emit(i + 1)
            print(f"[NMR Thread] Current scan = {i + 1} / {repeats}")
            ch1_data = self.generate_test_data()
            ch2_data = self.generate_test_data()
            self.data_out.emit(ch1_data, ch2_data)

            time.sleep(0.2)

        print("[NMR Thread] Dummy code finished")
        self.finished.emit()

    def prepare_device(self, sequence) -> None:


        # Write command to SDR14 registers
        for key, value in sequence.convert_to_dict().items():
            if key == "name":
                print(f"Parsing sequence: {value}")
            elif key in ["TX_phase", "RX_phase"]:
                print(f"Writing {key} with mask != 0, value = {value}")
            else:
                print(f"Writing {key} with mask = 0, value = {value}")

    @staticmethod
    def generate_test_data():
        l = 65536
        return np.random.random(l)

class PPMSController(QObject):

    finished = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.PPMS = PPMS()
        print("[PPMS Thread] __init__()")

    @pyqtSlot(object)
    def run_command(self, command) -> None:
        print(f"[PPMS Thread] Running dummy code with command = {command}")
        time.sleep(2)

        print("[PPMS Thread] Dummy code finished")
        self.finished.emit()

