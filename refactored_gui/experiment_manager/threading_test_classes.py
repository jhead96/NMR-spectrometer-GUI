from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import time


class NMRThreadTester(QObject):

    finished = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self.parameter = 0
        print("[NMR Thread] __init__()")

    @pyqtSlot(int)
    def set_parameter(self, value: int) -> None:
        self.parameter = value
        print(f"[NMR Thread] Parameter changed to {value}")

    @pyqtSlot()
    def test_method(self) -> None:
        print(f"[NMR Thread] Running dummy code with parameter = {self.parameter}")
        time.sleep(10)
        print("[NMR Thread] Dummy code finished")
        self.finished.emit(self.parameter)


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
