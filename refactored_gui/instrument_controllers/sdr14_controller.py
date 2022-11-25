import os
import sys
import ctypes as ct
from ctypes.util import find_library

class SDR14():

    def __init__(self, api_path: str = "\\GUI_pyQt\\refactored_gui\\instrument_controllers\\ADQAPI.dll") -> None:
        self.api_path = api_path
        self.api = self.retrieve_api()

    def retrieve_api(self) -> ct.CDLL:
        try:
            api =  ct.cdll.LoadLibrary(self.api_path)

        except WindowsError as ex:
            print(ex)
            print("Exiting...")
            sys.exit()
        
        return api


    def create_control_unit(self):
        


x = SDR14()
# print(find_library(r"\\adf.bham.ac.uk\eps\prhome21\J\JXH1264\Research\FPGA Development\NMR-spectrometer-GUI\NMR-spectrometer-GUI\GUI_pyQt\refactored_gui\instrument_controllers\ADQAPI.dll"))


