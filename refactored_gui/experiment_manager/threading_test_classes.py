from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from refactored_gui.instrument_controllers.sdr14_controller import SDR14
import time


class NMRThreadTester(QObject):

    finished = pyqtSignal()
    expt_progress = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self.spectrometer = SDR14()
        print("[NMR Thread] __init__()")

    @pyqtSlot(object)
    def run_command(self, command) -> None:
        self.prepare_device(command.sequence)
        print(f"[NMR Thread] Running dummy code with command = {command}")
        for i in range(0, 10):
            print(f"[NMR Thread] Current scan = {i + 1}")
            time.sleep(5)

        print("[NMR Thread] Dummy code finished")
        self.finished.emit()

    def prepare_device(self, sequence) -> None:
        # Write command to SDR14 registers
        for key, value in sequence.convert_to_dict().items():
            if key == "name":
                continue
            elif key in ["TX_phase", "RX_phase"]:
                print(f"Writing {key} with mask != 0")
            else:
                print(f"Writing {key} with mask = 0")





class PPMSThreadTester(QObject):

    finished = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self.parameter = 0
        print("[PPMS Thread] __init__()")

    @pyqtSlot(int)
    def set_parameter(self, value: int) -> None:
        self.parameter = value
        print(f"[PPMS Thread] Parameter changed to {value}")

    @pyqtSlot()
    def test_method(self) -> None:
        print(f"[PPMS Thread] Running dummy code with parameter = {self.parameter}")
        time.sleep(10)
        print("[PPMS Thread] Dummy code finished")
        self.finished.emit(self.parameter)
