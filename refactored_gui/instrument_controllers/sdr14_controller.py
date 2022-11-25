import os
import sys
import ctypes as ct


class SDR14():

    def __init__(self, api_path: str = r"M:\Research\NEW FPGA development\NMR spectrometer GUI\refactored_gui\instrument_controllers\ADQAPI.dll") -> None:
        self.api_path = api_path

        # Get api and assign control unit and device number
        self.api = self.retrieve_api()
        self.cu = self.create_control_unit()
        self.device_number = self.get_device_number()

        # Set default return types
        self.set_default_types()

        # Initialise device registers
        self.num_registers = 16
        self.initialise_registers()

    def retrieve_api(self) -> ct.CDLL:


        api = ct.cdll.LoadLibrary(self.api_path)

        """except OSError as ex:
            print(ex)
            print("Invalid ADQAPI.dll filepath or ADQ software development kit not installed!")
            print("Exiting...")
            sys.exit()"""

        return api

    def create_control_unit(self):

        # Creates and returns control unit
        cu = ct.c_void_p(self.api.CreateADQControlUnit())
        self.api.ADQControlUnit_FindDevices(cu)

        return cu

    def get_device_number(self):
        return 0

    def get_dev_info(self):
        pass

    def set_default_types(self) -> None:
        self.api.CreateADQControlUnit.restype = ct.c_void_p
        self.api.ADQ_WriteUserRegister.argtypes = [ct.c_void_p, ct.c_int, ct.c_int, ct.c_int,
                                                   ct.c_uint32, ct.c_uint32, ct.c_void_p]

    def initialise_registers(self) -> None:

        for i in range(0, self.num_registers):
            if not self.write_register(i, 0):
                print(f"Error writing to register {i}, exiting...")
                break

        print("All registers initialised to 0")

    def read_register(self, reg_number: int) -> bool:

        data_response = ct.c_uint32()   # Assign read back value type
        conf = self.api.ADQ_WriteUserRegister(self.cu, self.device_number, 0,
                                              reg_number, ct.byref(data_response))

        if conf:
            print(f"Register {reg_number} = {data_response.value}")
        else:
            print("Read unsuccessful!")

        return conf

    def write_register(self, reg_number: int, data: int, mask: int = 0) -> bool:
        data_write = ct.c_uint32(data)  # Convert to ctype unsigned integer
        data_response = ct.c_uint32()   # Assign read back value type
        conf = self.api.ADQ_WriteUserRegister(self.cu, self.device_number, 0,
                                              reg_number, mask, data_write, ct.byref(data_response))

        if conf:
            print(f"Register {reg_number} = {data_response.value}")
        else:
            print("Write unsuccessful!")
        return conf

    def enable_device(self):
        self.write_register(0, 1)

    def disable_device(self):
        self.write_register(0, 0)

