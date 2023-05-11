import time
import logging

import ctypes as ct
from dataclasses import dataclass
from enum import Enum

import numpy as np


class SDR14:

    def __init__(self, api_path: str = r"M:\Research\NEW FPGA development\NMR spectrometer GUI\refactored_gui\instrument_controllers\ADQAPI.dll") -> None:
        self.api_path = api_path

        # Initialise logger
        self.logger = self.initialise_logger()
        # Get api
        self.api = self.retrieve_api()

        # Handle no API found
        if self.api is None:
            return

        # Set default return types
        self.set_default_types()

        self.cu = self.create_control_unit()

        # Poll connected devices
        self.device_number = self.get_connected_devices()


        # Initialise device registers
        self.num_registers = 16
        self.initialise_registers()

        # Initialise reg function -> reg number look-up
        self.register_lookup = {'frequency': 1, 'TX_phase': -1, 'RX_phase': -1,
                                'p1': 2, 'p2': 3, 'p3': 4, 'g1': 5, 'g2': 6, 'rec': 7}
        self.register_mask = {'TX_phase': 0, 'RX_phase': 0}
        # Initialise acquisition parameters
        self.initial_parameters, self.acquisition_parameters = self.initialise_acquisition_parameters()

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

    def retrieve_api(self) -> ct.CDLL:
        """
        Loads ADQAPI from the designated filepath.
        :return: The api object from ctypes.
        """

        try:
            api = ct.cdll.LoadLibrary("ADQAPI.dll")
        except OSError as ex:
            self.logger.error(ex)
            self.logger.error("Invalid ADQAPI.dll filepath or ADQ software development kit not installed!")
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

    def get_connected_devices(self):
        number_of_devices = self.api.ADQControlUnit_NofADQ(self.cu)
        number_of_sdr14 = self.api.ADQControlUnit_NofSDR14(self.cu)

        if number_of_sdr14 != 1:
            self.logger.error("Invalid number of SDR14's connected, closing...")
            self.delete_control_unit()

        self.logger.info(f"Number of SDR14's detected: {number_of_sdr14}")
        return 1

    def delete_control_unit(self):
        """
        Deletes the control unit for the connected SDR14. Call when turning off device.
        :return:
        """

        conf = self.api.DeleteADQControlUnit(self.cu)

        if conf:
            self.logger.info("ADQ Control unit deleted!")

    def get_device_number(self):
        """
        Gets the device number of the connected SDR14 required for api calls.
        :return: The device number.
        """
        return 1

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
        self.api.ADQControlUnit_FindDevices.argtypes = [ct.c_void_p]
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

        self.logger.info("All registers initialised to 0")

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
                                              reg_number, 0xFFFFFF, 0, ct.byref(data_response))

        if conf:
            self.logger.info(f"Register {reg_number} = {data_response.value}")
        else:
            self.logger.warning("Read unsuccessful!")

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
            self.logger.info(f"Register {reg_number} = {data_response.value}")
        else:
            self.logger.warning("Write unsuccessful!")

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

    def set_clock_source(self, clock_source) -> None:

        valid = self.api.ADQ_SetClockSource(self.cu, self.device_number, clock_source.value)
        if valid:
            self.logger.info(f"Clock source set to INTERNAL = {clock_source.value}")
        else:
            self.logger.warning("Error setting clock source!")

    def set_trigger_mode(self, trigger_type) -> None:

        valid = self.api.ADQ_SetTriggerMode(self.cu, self.device_number, trigger_type.value)
        if valid:
            self.logger.info(f"Trigger set to {trigger_type} = {trigger_type.value}")
        else:
            self.logger.warning("Failed to set trigger")

    def set_external_trig_edge(self):
        valid = self.api.ADQ_SetExternTrigEdge(self.cu, self.device_number, 1)

        if valid:
            self.logger.info(f"External trigger edge set to RISING")
        else:
            self.logger.warning("Failed to set external trigger edge!")

    def set_pretrigger(self, samples: int = 0) -> None:

        valid = self.api.ADQ_SetPreTrigSamples(self.cu, self.device_number, samples)

        if valid:
            self.logger.info(f"Pretrigger = {samples} samples")
        else:
            self.logger.warning("Failed to set pretrigger")

    def set_trigger_delay(self, samples: int = 0) -> None:

        valid = self.api.ADQ_SetTriggerDelay(self.cu, self.device_number, samples)

        if valid:
            self.logger.info(f"Trigger delay = {samples} samples")
        else:
            self.logger.warning("Failed to set trigger delay")

    def setup_MR_mode(self) -> None:

        # Setup SDR-14 for MultiRecord acquisition

        valid = self.api.ADQ_MultiRecordSetup(self.cu, self.device_number,
                                                 self.acquisition_parameters.num_of_records,
                                                 self.acquisition_parameters.samples_per_record)
        if valid:
            self.logger.info(f"MultiRecord parameters changed \n"
                  f" Number of records: {self.acquisition_parameters.num_of_records}\n"
                  f" Samples per record: {self.acquisition_parameters.samples_per_record}")
        else:
            self.logger.warning("Error while setting MR settings!")

    def arm_MR_trigger(self):
        # Deactivate trigger
        trig_disarmed = self.api.ADQ_DisarmTrigger(self.cu, self.device_number)

        if trig_disarmed:
            self.logger.info("Trigger disarmed")
        else:
            self.logger.warning("Error while disarming trigger!")

        # Activate trigger
        trig_armed = self.api.ADQ_ArmTrigger(self.cu, self.device_number)
        if trig_armed:
            self.logger.info("Trigger armed")
        else:
            self.logger.warning("Error while arming trigger!")


    def MR_acquisition(self) -> (np.ndarray, np.ndarray):

        # Setup SDR14
        self.setup_MR_mode()
        self.set_clock_source(ClockSource.INTERNAL)
        self.set_trigger_mode(TriggerMode.EXTERNAL)
        #self.set_external_trig_edge()

        self.set_trigger_delay()


        # Arm trigger
        self.arm_MR_trigger()


        # Acquire data
        self.enable_device()
        time.sleep(1)
        self.disable_device()
        self.logger.info('Data acquisition successful!')

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
            self.logger.info('Data retrieved successfully')

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
    INTERNAL = 0
    EXTERNAL = 2


class TriggerMode(Enum):
    SOFTWARE = 1
    EXTERNAL = 2
    LEVEL = 3
    INTERNAL = 4