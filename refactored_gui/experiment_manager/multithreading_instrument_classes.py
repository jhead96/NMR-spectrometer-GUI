from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from refactored_gui.instrument_controllers.sdr14_controller import SDR14
from refactored_gui.instrument_controllers.ppms_controller import PPMS
from datetime import datetime
from abc import ABC, abstractmethod
import time
import logging
import numpy as np
from enum import Enum


class FinalMeta(type(ABC), type(QObject)):
    pass


class SpectrometerThreadController(ABC):

    @abstractmethod
    def prepare_device(self, sequence):
        pass

    @abstractmethod
    def run_command(self, command):
        pass

    @abstractmethod
    def save_data(self, ch1_data: np.ndarray, ch2_data: np.ndarray, repeats: int, seq_name: str):
        pass

    @abstractmethod
    def set_save_dir(self, save_dir: str):
        pass

    @abstractmethod
    def shutdown_thread(self):
        pass


class SpectrometerControllerDummy(SpectrometerThreadController, QObject, metaclass=FinalMeta):

    finished = pyqtSignal()
    current_repeat = pyqtSignal(int, str)
    data_out = pyqtSignal(int, object, object, str)
    safe_to_close = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.logger = self.initialise_logger()
        self.save_dir = None
        print("NMR thread started")

    @staticmethod
    def initialise_logger() -> logging.Logger:

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Log formatting
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(log_format, date_format)

        # File logging
        file_handler = logging.FileHandler("logs.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        # Console logging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)

        return logger

    @pyqtSlot(object)
    def run_command(self, command) -> None:
        self.prepare_device(command.sequence)
        repeats = command.repeats
        seq_name = command.sequence_filepath.split('/')[-1][:-4]
        print(f"[NMR Thread] Running dummy code with command = {command}")
        for i in range(0, repeats):
            self.current_repeat.emit(i + 1, seq_name)
            print(f"[NMR Thread] Current scan = {i + 1} / {repeats}")
            ch1_data = self.generate_test_data()
            ch2_data = self.generate_test_data()
            self.data_out.emit(i + 1, ch1_data, ch2_data, self.save_dir)
            self.save_data(ch1_data, ch2_data, i+1, seq_name)
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

    def save_data(self, ch1_data: np.ndarray, ch2_data: np.ndarray, repeat: int, seq_name: str) -> None:
        np.savetxt(f"{self.save_dir}/{seq_name}_{repeat}.txt", (ch1_data, ch2_data))

    @pyqtSlot()
    def shutdown_thread(self) -> None:
        print("[NMR Thread] Disconnecting SDR14")
        self.safe_to_close.emit()

    @staticmethod
    def generate_test_data() -> np.ndarray:
        l = 65536
        return np.random.random(l)


class SpectrometerController(SpectrometerThreadController, QObject, metaclass=FinalMeta):

    finished = pyqtSignal()
    current_repeat = pyqtSignal(int, str)
    data_out = pyqtSignal(int, object, object, str)
    safe_to_close = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.SDR14 = SDR14
        self.save_dir = None
        print("[NMR Thread] __init__()")

    @pyqtSlot(object)
    def run_command(self, command) -> None:
        self.prepare_device(command.sequence)
        repeats = command.repeats
        seq_name = command.sequence_filepath.split('/')[-1][:-4]
        print(f"[NMR Thread] Running command: {command}")
        for i in range(0, repeats):
            self.current_repeat.emit(i + 1, seq_name)
            print(f"[NMR Thread] Current scan = {i + 1} / {repeats}")
            ch1_data, ch2_data = self.SDR14.MR_acquisition()
            self.data_out.emit(i + 1, ch1_data, ch2_data, self.save_dir)
            self.save_data(ch1_data, ch2_data, i + 1, seq_name)
            time.sleep(0.5)

        print("[NMR Thread] Dummy code finished")
        self.finished.emit()

    def prepare_device(self, sequence) -> None:

        # Write sequence to SDR14 registers
        for key, value in sequence.convert_to_dict().items():
            if key == "name":
                print(f"Parsing sequence: {value}")
            elif key in ["TX_phase", "RX_phase"]:
                register_number = self.SDR14.register_lookup[key]
                mask = self.SDR14.register_mask[key]
                self.SDR14.write_register(register_number, value, mask=mask)
            else:
                register_number = self.SDR14.register_lookup[key]
                self.SDR14.write_register(register_number, value)

    @pyqtSlot(str)
    def set_save_dir(self, save_dir: str) -> None:
        self.save_dir = save_dir

    def save_data(self, ch1_data: np.ndarray, ch2_data: np.ndarray, repeat: int, seq_name: str) -> None:
        np.savetxt(f"{self.save_dir}/{seq_name}_{repeat}.txt", (ch1_data, ch2_data))

    @pyqtSlot()
    def shutdown_thread(self) -> None:
        print("[NMR Thread] Disconnecting SDR14")
        self.safe_to_close.emit()


class PPMSThreadController(ABC):

    @abstractmethod
    def run_command(self, command):
        pass

    @abstractmethod
    def poll_PPMS(self):
        pass

    @abstractmethod
    def log_data_to_file(self, T: float, H: float, seq_name: str) -> None:
        pass

    @abstractmethod
    def set_save_dir(self, save_dir: str) -> None:
        pass

    @abstractmethod
    def shutdown_thread(self):
        pass


class PPMSController(PPMSThreadController, QObject, metaclass=FinalMeta):


    def __init__(self):
        super().__init__()
        self.PPMS = PPMS()
        self.save_dir = None
        print("[PPMS Thread] __init__()")


class PPMSControllerDummy(PPMSThreadController, QObject, metaclass=FinalMeta):

    PPMS_data_out = pyqtSignal(float, float)
    finished = pyqtSignal()
    safe_to_close = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.logger = self.initialise_logger()
        self.save_dir = None
        self.logger.info("PPMS thread started")

    @staticmethod
    def initialise_logger() -> logging.Logger:

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Log formatting
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(log_format, date_format)

        # File logging
        file_handler = logging.FileHandler("logs.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        # Console logging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)

        return logger

    @pyqtSlot(object)
    def run_command(self, command) -> None:
        print(f"[PPMS Thread] Running dummy code with command = {command}")
        time.sleep(2)

        print("[PPMS Thread] Dummy code finished")
        self.finished.emit()

    @pyqtSlot(str)
    def set_save_dir(self, save_dir: str) -> None:
        self.save_dir = save_dir

    @pyqtSlot(str)
    def poll_PPMS(self, seq_name) -> None:
        T = self.get_T()
        H = self.get_H()
        self.log_data_to_file(T, H, seq_name)
        self.PPMS_data_out.emit(T, H)

    @staticmethod
    def get_T() -> float:
        return np.random.random(1)[0]

    @staticmethod
    def get_H() -> float:
        return np.random.random(1)[0]

    def log_data_to_file(self, T: float, H: float, seq_name: str) -> None:
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H:%M:%S")

        with open(f"{self.save_dir}/PPMS_conditions_{seq_name}.txt", "a") as f:
            f.write(f"{timestamp},{T},{H}\n")

    @pyqtSlot()
    def shutdown_thread(self) -> None:
        print("[PPMS Thread] Disconnecting PPMS")
        self.safe_to_close.emit()