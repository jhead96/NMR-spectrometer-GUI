from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from refactored_gui.instrument_controllers.sdr14_controller import SDR14
from refactored_gui.instrument_controllers.ppms_controller import PPMS
from datetime import datetime
import time
import numpy as np


class SpectrometerController(QObject):

    finished = pyqtSignal()
    current_repeat = pyqtSignal(int)
    data_out = pyqtSignal(int, object, object)
    safe_to_close = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.spectrometer = SDR14()
        self.save_dir = None
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
            self.data_out.emit(i + 1, ch1_data, ch2_data)
            self.save_data(ch1_data, ch2_data, i+1)
            time.sleep(0.5)

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

    @pyqtSlot(str)
    def set_save_dir(self, save_dir: str) -> None:
        self.save_dir = save_dir

    def save_data(self, ch1_data: np.ndarray, ch2_data: np.ndarray, repeat: int) -> None:
        np.savetxt(f"{self.save_dir}/{repeat}.txt", (ch1_data, ch2_data))

    @pyqtSlot()
    def close_thread(self) -> None:
        print("[NMR Thread] Disconnecting SDR14")

    @staticmethod
    def generate_test_data() -> np.ndarray:
        l = 65536
        return np.random.random(l)


class PPMSController(QObject):

    PPMS_data_out = pyqtSignal(float, float)
    finished = pyqtSignal()
    safe_to_close = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.PPMS = PPMS()
        self.save_dir = None
        print("[PPMS Thread] __init__()")

    @pyqtSlot(object)
    def run_command(self, command) -> None:
        print(f"[PPMS Thread] Running dummy code with command = {command}")
        time.sleep(2)

        print("[PPMS Thread] Dummy code finished")
        self.finished.emit()

    @pyqtSlot(str)
    def set_save_dir(self, save_dir: str) -> None:
        self.save_dir = save_dir

    @pyqtSlot()
    def poll_PPMS(self) -> None:
        T = self.get_T()
        H = self.get_H()
        self.log_data_to_file(T, H)
        self.PPMS_data_out.emit(T, H)

    @staticmethod
    def get_T() -> float:
        return np.random.random(1)[0]

    @staticmethod
    def get_H() -> float:
        return np.random.random(1)[0]

    def log_data_to_file(self, T: float, H: float) -> None:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H:%M:%S")


        with open(f"{self.save_dir}/PPMS_conditions.txt", "a") as f:
            f.write(f"{timestamp},{T},{H}\n")

    @pyqtSlot()
    def close_thread(self) -> None:
        print("[PPMS Thread] Disconnecting PPMS")