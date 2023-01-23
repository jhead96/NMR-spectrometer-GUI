import os
import sys
import ctypes as ct
from dataclasses import dataclass
from enum import Enum

import numpy as np


class SDR14:

    def __init__(self, api_path: str = r"M:\Research\NEW FPGA development\NMR spectrometer GUI\refactored_gui\instrument_controllers\ADQAPI.dll") -> None:
        self.api_path = api_path

        # Get api
        self.api = self.retrieve_api()

        # Handle no API found
        if self.api is None:
            return

        self.cu = self.create_control_unit()
        self.device_number = self.get_device_number()

        # Set default return types
        self.set_default_types()

        # Initialise device registers
        self.num_registers = 16
        self.initialise_registers()

        # Initialise acquisition parameters
        self.initial_parameters, self.acquisition_parameters = self.initialise_acquisition_parameters()

    def retrieve_api(self) -> ct.CDLL:
        """
        Loads ADQAPI from the designated filepath.
        :return: The api object from ctypes.
        """

        try:
            api = ct.cdll.LoadLibrary(self.api_path)
        except OSError as ex:
            print(ex)
            print("Invalid ADQAPI.dll filepath or ADQ software development kit not installed!")
            print("ADQAPI functions disabled!")
            api = None

        return api

    def create_control_unit(self):
        """
        Creates a control unit required for api calls.
        :return: Control unit.
        """

        # Creates and returns control unit
        cu = ct.c_void_p(self.api.CreateADQControlUnit())
        self.api.ADQControlUnit_FindDevices(cu)

        return cu

    def delete_control_unit(self):
        """
        Deletes the control unit for the connected SDR14. Call when turning off device.
        :return:
        """

        conf = self.api.DeleteADQControlUnit(self.cu)

        if conf:
            print("Control unit deleted!")

    def get_device_number(self):
        """
        Gets the device number of the connected SDR14 required for api calls.
        :return: The device number.
        """
        return 0

    def get_dev_info(self):
        """
        Logs device info.
        :return:
        """
        pass

    def set_default_types(self) -> None:
        """
        Sets default return types for api calls.
        :return:
        """
        self.api.CreateADQControlUnit.restype = ct.c_void_p
        self.api.ADQ_WriteUserRegister.argtypes = [ct.c_void_p, ct.c_int, ct.c_int, ct.c_int,
                                                   ct.c_uint32, ct.c_uint32, ct.c_void_p]

    def initialise_registers(self) -> None:
        """
        Initialises all device registers to 0.
        :return:
        """

        for i in range(self.num_registers):
            if not self.write_register(i, 0):
                print(f"Error writing to register {i}, exiting...")
                break

        print("All registers initialised to 0")

    @staticmethod
    def initialise_acquisition_parameters() -> tuple:
        initial_parameters = [10, 1024 * 2, 4, 2, 0, 10000, 0, 0, 1, 65536]
        acquisition_parameters = AcquisitionParameters(*initial_parameters)

        return initial_parameters, acquisition_parameters

    def read_register(self, reg_number: int) -> bool:
        """
        Reads the specified register.
        :param reg_number: Register number to read.
        :return: True if read successful.
        """

        data_response = ct.c_uint32()   # Assign read back value type
        conf = self.api.ADQ_WriteUserRegister(self.cu, self.device_number, 0,
                                              reg_number, ct.byref(data_response))

        if conf:
            print(f"Register {reg_number} = {data_response.value}")
        else:
            print("Read unsuccessful!")

        return conf

    def write_register(self, reg_number: int, data: int, mask: int = 0) -> bool:
        """
        Writes to specified register.
        :param reg_number: Number of register to be written to.
        :param data: Data to be written to register.
        :param mask: Binary mask to specify bits to be written to.
        :return: True if write successful.
        """
        data_write = ct.c_uint32(data)  # Convert to ctype unsigned integer
        data_response = ct.c_uint32()   # Assign read back value type
        conf = self.api.ADQ_WriteUserRegister(self.cu, self.device_number, 0,
                                              reg_number, mask, data_write, ct.byref(data_response))

        if conf:
            print(f"Register {reg_number} = {data_response.value}")
        else:
            print("Write unsuccessful!")
        return conf

    def enable_device(self) -> None:
        """
        Enables device by writing '1' to user register 0. Must be called to start any experiment.
        :return:
        """

        self.write_register(0, 1)

    def disable_device(self) -> None:
        """
        Disables device by writing '0' to user register 0.
        :return:
        """
        self.write_register(0, 0)

    def set_clock_source(self) -> None:

        valid = self.__api.ADQ_SetClockSource(self.__cu, self.device_number, ClockSource.INTERNAL)
        if valid:
            print("Clock source set to INTERNAL")
        else:
            print("Error setting clock source!")

    def set_trigger_mode(self, trigger_type: TriggerMode) -> None:

        valid = self.__api.ADQ_SetTriggerMode(self.__cu, self.device_number, trigger_type)
        if valid:
            print(f"Trigger set to {trigger_type}")
        else:
            print('Failed to set trigger')

    def set_pretrigger(self, samples: int):

        valid = self.__api.ADQ_SetPreTrigSamples(self.__cu, self.device_number, samples)

        if valid:
            print(f"Pretrigger = {samples} samples")
        else:
            print('Failed to set pretrigger')

    def set_trig_delay(self, samples: int):

        valid = self.__api.ADQ_SetTriggerDelay(self.__cu, self.device_number, samples)

        if valid:
            print(f"Trigger delay = {samples} samples")
        else:
            print('Failed to set trigger delay')

    def setup_MR_mode(self) -> None:

        # Setup SDR-14 for MultiRecord acquisition

        valid = self.__api.ADQ_MultiRecordSetup(self.__cu, self.device_number,
                                                 self.acquisition_parameters.num_of_records,
                                                 self.acquisition_parameters.samples_per_record)
        if valid:
            print(f"MultiRecord parameters changed \n"
                  f" Number of records: {self.acquisition_parameters.num_of_records}\n"
                  f" Samples per record: {self.acquisition_parameters.samples_per_record}")
        else:
            print("Error while setting MR settings!")

    def arm_MR_trigger(self):
        # Deactivate trigger
        self.__api.ADQ_DisarmTrigger(self.__cu, self.device_number)
        # Activate trigger
        trig_armed = self.__api.ADQ_ArmTrigger(self.__cu, self.device_number)
        if trig_armed:
            print('Trigger armed')

    def MR_acquisition(self) -> (np.ndarray, np.ndarray):

        # Setup SDR14
        self.setup_MR_mode()
        self.set_clock_source()
        self.set_trigger_mode()
        self.set_pretrigger()
        self.set_trigger_delay()

        # Arm trigger
        self.arm_MR_trigger()

        # Acquire data
        self.enable_dev()
        time.sleep(1)
        self.disable_dev()
        print('Data acquisition successful!')

        # Initialise buffers
        max_channels = 2
        target_buffers = (ct.POINTER(
            ct.c_int16 * self.acquisition_parameters.samples_per_record * self.acquisition_parameters.num_of_records)
                          * max_channels)()
        # Retrieve data
        for buf_pntr in target_buffers:
            buf_pntr.contents = (
                    ct.c_int16 * self.acquisition_parameters.samples_per_record *
                    self.acquisition_parameters.num_of_records)()

        ADQ_TRANSFER_MODE = 0  # Default mode
        ADQ_CHANNELS_MASK = 0x3  # Read from both channels

        status = self.api.ADQ_GetData(self.cu, self.device_number, target_buffers,
                                        self.acquisition_parameters.samples_per_record * self.acquisition_parameters.num_of_records,
                                        2, 0, self.acquisition_parameters.num_of_records, ADQ_CHANNELS_MASK,
                                        0, self.acquisition_parameters.samples_per_record, ADQ_TRANSFER_MODE)
        if status:
            print('Data retrieved successfully')

        ch1_data = np.frombuffer(target_buffers[0].contents[0], dtype=np.int16)
        ch2_data = np.frombuffer(target_buffers[1].contents[0], dtype=np.int16)

        # Disarm trigger and close MR mode
        self.api.ADQ_DisarmTrigger(self.cu, self.device_number)
        self.api.ADQ_MultiRecordClose(self.cu, self.device_number)

        return ch1_data, ch2_data


@dataclass()
class AcquisitionParameters:
    buffers: int
    samples_per_buffer: int
    sample_skip: int
    bytes_per_sample: int
    clock_source: int
    total_nof_buffers: int
    records_fetched: int
    overflows: int
    num_of_records: int
    samples_per_record: int

    def set_acquisition_parameters(self, buffers: int, samples_per_buffer: int, sample_skip: int,
                                   bytes_per_sample: int, clock_source: int, total_nof_buffers: int,
                                   records_fetched: int, overflows: int, num_of_records: int,
                                   samples_per_record: int) -> None:
        self.buffers = buffers
        self.samples_per_buffer = samples_per_buffer
        self.sample_skip = sample_skip
        self.bytes_per_sample = bytes_per_sample
        self.clock_source = clock_source
        self.total_nof_buffers = total_nof_buffers
        self.records_fetched = records_fetched
        self.overflows = overflows
        self.num_of_records = num_of_records
        self.samples_per_record = samples_per_record


class ClockSource(Enum):
    pass
    INTERNAL = 0
    EXTERNAL = 2


class TriggerMode(Enum):
    SOFTWARE = 1
    EXTERNAL = 2
    LEVEL = 3
    INTERNAL = 4


x = SDR14()