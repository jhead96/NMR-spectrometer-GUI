import ctypes as ct
import os, time
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum

class TrigMode(Enum):
    SOFTWARE = 1
    EXTERNAL = 2
    LEVEL = 3
    INTERNAL = 4

class sdr14:
    """
    SDR14 tools - v1.1
    ===

    Key tools for accessing and running the SDR14 with the UoBFNS.
        Provides a class (sdr14_tools) to manage the ADQ api functions
        through simplified functions.

    Invoked using sdr14_tools() with optional arguments

    Arguments
    ---------
        str: lib_dir (opt): API library path
            default = "", depending on os will use:
                - "ADQAPI.dll" for windows
                - "libadq.so" for *NIX based systems
        bool: adq_logs (opt): Create trace log file generated by device
            default = False
        bool: quiet (opt): Default to muting printed feedback messages
            default = False
            Can be overidden after initialisation using the
            'set_global_quiet()' method

    Provides
    --------

    """

    def __init__(self, lib_dir="", adq_logs=False, quiet=False):
        self.__quiet = quiet  # Set global quiet state
        self.__api = self.__load_api(lib_dir)  # Load api as private object
        if adq_logs:  # Enable error logging to file
            conf = self.__api.ADQControlUnit_EnableErrorTrace(self.__cu,
                                                              3,
                                                              ".")
            if not quiet and conf:
                print("Saving ADQ error trace logs")
        self.__default_type_config()  # Assign default IO types
        self.__cu = self.__create_cu()  # Create control unit as private object
        number_of_devices = self.connected_adq()  # List connected Devices
        if number_of_devices > 1:  # Ensure only one device is connected
            self.delete_cu()
            raise OSError("Too many devices detected,\
                          disconnect all other ADQ devices")
        elif number_of_devices == 0:
            self.delete_cu()
            raise OSError("No devices detected")
        self.device_number = 1  # Device to use (only 1 device)
        self.cu = self.__cu
        self.api = self.__api
        self.device_type = self.__api.ADQ_GetADQType(self.__cu, self.device_number)
        if self.device_type != 14:
            self.delete_cu()
            raise OSError("Connected device is not an SDR14, exiting")
        self.__api.ADQ_SetClockSource(self.__cu, self.device_number, 0)

        print(self.device_type)


        self.reg_cache = [None] * 16  # Create user register data cache array
        self.reg_reset()  # Load default values into SDR14s user register

        ### Create additional objects for data recording ###
        self.stream_cfg_data = self.stream_config_struct()

    def set_global_quiet(self, setting, quiet=None):
        """
        Allows global quiet setting to be updated.

        Arguments
        ---------
            bool: setting - True to suppress responses.

        Returns
        -------
            int: success - 1 for success, 0 for failure (ie invalid input)
        """
        quiet = self.__qtest(quiet)
        if type(setting) == bool:
            self.__quiet = setting
            if setting == self.__quiet:
                if not quiet:
                    print("Global quiet set to {}".format(setting))
                return 1
            else:
                if not quiet:
                    print("Failed to set global quiet. \
                          Set to {}".format(self.__quiet))
                return 0
        elif type(setting) == int:
            if setting == 1:
                setting = True
            elif setting == 0:
                setting = False
            else:
                if not quiet:
                    print("Failed to set global quiet \
                          Set to {}".format(self.__quiet))
                return 0
        else:
            if not quiet:
                print("Argument must be boolean (True/False)")
            return 0

    def read_global_quiet(self, quiet: bool = None) -> bool:
        """
        Read the current global quiet setting (see set_global_quiet)

        Returns
        -------
            bool: setting - Current global quiet setting as a boolean
        """
        quiet = self.__qtest(quiet)
        if not quiet:
            print("Current global quiet setting: {}".format(self.__quiet))
        return self.__quiet

    def __qtest(self, quiet: bool) -> bool:
        """
        Quiet test, allows argument to override global quiet

        Arguments
        ---------
            bool/nonetype: quiet - Requited quiet setting

        Returns
        -------
            bool: quiet - Quiet setting to use
        """
        return ((quiet == None and self.__quiet) or quiet)

    def __failed(self, task: str, quiet: bool) -> bool:
        """
        Convenience function to return a fail message

        Arguments
        ---------
            str: task - Name of the task that failed

        Returns
        -------
            int: 0
        """
        if not quiet:
            print("{} FAILED".format(task))
        return 0

    def __load_api(self, lib_dir: str = None, quiet: bool = None):
        """
        Load ADQ library and configure response types

        Arguments
        ---------
            str: lib_dir (opt) - ADQAPI file location
            bool: quiet - Global quiet override
        """
        quiet = self.__qtest(quiet)

        # If no adq library is provided, use default based on detected OS
        if not lib_dir:
            if os.name == "nt":  # If Windows use dll
                lib_dir = "ADQAPI.dll"
                if not quiet:
                    print("Windows detected, loading ADQAPI.dll...")
            else:
                lib_dir = "libadq.so"
                if not quiet:
                    print("Non-nt system, Loading libadq.so...")

        try:
            api = ct.cdll.LoadLibrary("ADQAPI.dll")
            if not quiet:
                print("SUCCESS")
                print("ADQAPI loaded, \
                       revision {:d}".format(api.ADQAPI_GetRevision()))
            return api
        except OSError:
            if not quiet:
                print("Driver (ADQAPI.dll) file not found")
            raise Exception("The ADQAPI driver file could \
                            not be found... Exiting")

    def __default_type_config(self, quiet: bool =None):
        """
        Set API default input/output data types
        """
        quiet = self.__qtest(quiet)
        self.__api.CreateADQControlUnit.restype = ct.c_void_p
        self.__api.ADQ_GetRevision.restype = ct.c_void_p
        self.__api.ADQ_GetPtrStream.restype = ct.POINTER(ct.c_int16)
        self.__api.ADQControlUnit_FindDevices.argtypes = [ct.c_void_p]
        self.__api.ADQ_WriteUserRegister.argtypes = [ct.c_void_p,
                                                     ct.c_int,
                                                     ct.c_int,
                                                     ct.c_int,
                                                     ct.c_uint32,
                                                     ct.c_uint32,
                                                     ct.c_void_p]
        self.__api.ADQ_GetBoardSerialNumber.restype = ct.c_char_p
        self.__api.ADQ_GetBoardProductName.restype = ct.c_char_p
        self.__api.ADQ_GetTemperature.restype = ct.c_int
        if not quiet:
            print("""
Argument and response types set as follows (ct -> ctypes):
api.CreateADQControlUnit.restype = ct.c_void_p
api.ADQ_GetRevision.restype = ct.c_void_p
api.ADQ_GetPtrStream.restype = ct.POINTER(ct.c_int16)
api.ADQControlUnit_FindDevices.argtypes = [ct.c_void_p]
api.ADQ_WriteUserRegister.argtypes = [ct.c_int,
                                      ct.c_int,
                                      ct.c_uint32,
                                      ct.c_uint32,
                                      ct.c_void_p]
api.ADQ_GetBoardSerialNumber.restype = ct.c_char_p
api.ADQ_GetBoardProductName.restype = ct.c_char_p\n
""")

    def connected_adq(self, quiet: bool = None) -> int:
        """
        Poll the number of currently connected devices

        Returns
        -------
            int: number_of_devices - Current number of connected devices
        """
        quiet = self.__qtest(quiet)
        number_of_devices = self.__api.ADQControlUnit_NofADQ(self.__cu)
        number_of_sdr14 = self.__api.ADQControlUnit_NofSDR14(self.__cu)
        number_of_other = number_of_devices - number_of_sdr14
        if not quiet:
            print("Found {} ADQ Device(s):\
                  \n{} SDR14(s)\
                  \n{} Other\n".format(number_of_devices,
                                       number_of_sdr14,
                                       number_of_other))
        return number_of_devices

    def __create_cu(self, quiet: bool = None) -> ct.c_void_p:
        """
        Create control unit and find/assign connected devices to it.
        Private such that cu is not created without first deleting the
            existing control unit.

        Returns
        -------
            ct.c_void_p: cu - Pointer to device control unit
        """
        quiet = self.__qtest(quiet)
        # Creates and returns control unit, prints list of devices connected
        cu = ct.c_void_p(self.__api.CreateADQControlUnit())
        if not quiet:
            print("ADQ Control Unit created at pointer {}".format(cu.value))
        self.__api.ADQControlUnit_FindDevices(cu)
        return cu

    def delete_cu(self, quiet: bool = None) -> int:
        """
        Delete existing control unit

        Returns
        -------
            int: conf - 1 if success full
        """
        quiet = self.__qtest(quiet)
        if self.connected_adq(quiet=True):
            conf = self.__api.DeleteADQControlUnit(self.__cu)
            if conf and not quiet:
                print("Control Unit removed")
            elif not quiet:
                print("Remove Control Unit FAILED")
            return conf
        else:
            if not quiet:
                print("No Control Units to remove")
            return 0

    def reload_cu(self, quiet: bool = None):
        """
        Delete and re-create control unit
        """
        quiet = self.__qtest(quiet)
        self.delete_cu(quiet)
        self.__cu = self.__create_cu(quiet)

    def reg_write(self, register: int, data: int, mask: int = 0, quiet: bool = None) -> int:
        """
        Write a value to a specified user register

        Arguments
        ---------
            int: register - Register to write to
            int: data - Data to be written
            int: mask - 32-bit mask to apply to the data, 1 protects
                        current bits, 0 allows overwrite
            bool: quiet - Override global quiet

        Returns
        -------
            int: conf - 1 if successful
        """
        quiet = self.__qtest(quiet)
        data_write = ct.c_uint32(data)  # Convert to ctype unsigned integer
        data_response = ct.c_uint32()
        conf = self.__api.ADQ_WriteUserRegister(self.__cu,  # control unit
                                                # adq number
                                                self.device_number,
                                                # logic space target (SDR14=0)
                                                0,
                                                # register number
                                                register,
                                                # bitmask
                                                mask,
                                                # data to write
                                                data_write,
                                                # read back pointer
                                                ct.byref(data_response))
        if conf:
            self.reg_cache[register] = data_response.value
        if not quiet:
            print("reg{} written: {}".format(register,
                                             self.reg_cache[register]))
        return conf

    def enable_dev(self):
        """
        Enable device by writing 1 to the PC_Enable register (0).
        """
        self.reg_write(0, 1)

    def disable_dev(self):
        """
        Disable device by writing 0 to the PC_Enable register (0).
        """
        self.reg_write(0, 0)

    def reg_read(self, register: int, quiet: bool = None) -> int:
        """
        Read value from a specified user register. Also updates local cache

        Arguments
        ---------
            int: register - Register to read from

        Returns
        -------
            int: value - Value stored in register

        conf = self.reg_write(register, data, mask=0xFFFFFFFF, quiet=True)
        if not quiet:
            print("reg{} read: {}".format(register, self.reg_cache[register]))
        return self.reg_cache[register]
        """
        pass

    def reg_refresh(self, quiet:bool = None):
        """
        Pull all user register values from device
        """
        quiet = self.__qtest(quiet)
        for i in range(16):
            self.reg_read(i, True)
        if not quiet:
            print("\nCurrent user register contents")
            for i in range(16):
                print("reg{} read: {}".format(i, self.reg_cache[i]))

    def reg_reset(self, quiet:bool = None) -> int:
        """
        Default (initial) user_regiser values

        Returns
        -------
            int: conf - 1 if successful
        """
        quiet = self.__qtest(quiet)
        def_vals = [0,  # reg0
                    20 * 10 ** 6,  # reg1
                    0,  # reg2
                    0,  # reg3
                    0,  # reg4
                    0,  # reg5
                    0,  # reg6
                    0,  # reg7
                    65537,  # reg8
                    1,  # reg9
                    0,  # reg10
                    0,  # reg11
                    0,  # reg12
                    0,  # reg13
                    0,  # reg14
                    0]  # reg15
        i = 0
        conf = [False] * 16
        for val in def_vals:
            conf[i] = self.reg_write(i, val, quiet=quiet)
            i += 1
        if 0 or False in conf:
            return self.__failed("Loading default register values", quiet)
        else:
            if not quiet:
                print("Loaded default register values\n")
            return 1

    def read_temp(self, sensor_num: int) -> (float, str):
        temp = 0
        sensor_type = np.array(['Local: ', 'ADC 0: ', 'ADC 1: ', 'FPGA: ', 'PCB diode: ', 'Error!'])
        try:
            sensor = int(sensor_num)

            if 0 <= sensor <= 4:
                sensor_in = ct.c_uint(sensor)
                sensor_name = sensor_type[sensor]
                temp = self.__api.ADQ_GetTemperature(self.__cu, self.device_number, sensor_in) / 256
            else:
                print('Invalid sensor number')
                sensor_name = ''
            return temp, sensor_name

        except ValueError:
            print('Invalid sensor number')
            sensor_name = ''
            return temp, sensor_name

    class stream_config_struct:
        """
        Data structure to store data streaming variables
        """

        def __init__(self):
            self.nof_buffers = 10
            self.nof_samples_per_buffer = 1024 * 2
            self.sample_skip = 4
            self.bytes_per_sample = 2
            self.clock_source = 0
            self.total_nof_buffers = 10000
            self.records_fetched = 0
            self.overflows = 0
            self.num_of_records = 1
            self.samples_per_record = 65536

        def get_config(self):
            """
            Return current stored values for data streaming

            Returns
            -------
                int: nof_buffers - Number of buffers on device
                int: nof_samples_per_buffer - samples per buffer
                int: sample_skip - number of samples to skip per buffer
                int: bytes_per_sample - Always 2 (16-bit = 2 byte)
                int: clock_source - 0 is default
                int: total_nof_buffer - total records to collect
            """
            return self.nof_buffers, self.nof_samples_per_buffer, \
                   self.sample_skip, self.bytes_per_sample, \
                   self.clock_source, self.total_nof_buffers

        def set_config(self, total_records: int = None,
                       records_per_transfer: int = None,
                       samples_per_record: int = None) -> (bool, int):
            """
            Set configuration for data streaming

            Arguments
            ---------
                int: total_records (opt) - Set total records to collect
                int: records_per_transfer (opt) - set number of records
                                                  per transfer
                int: samples_per_record (opt) - set number of samples
                                                per record

            Returns
            -------
                bool: success - returns True if successful
                int: exit_code - reason for exit
            """
            try:
                for i in [total_records,
                          records_per_transfer,
                          samples_per_record]:
                    if i:
                        if float(i) - int(i):
                            raise ValueError("Config types must be int")
                if total_records:
                    self.total_nof_buffers = int(total_records)
                if records_per_transfer:
                    self.nof_buffers = int(records_per_transfer)
                if samples_per_record:
                    self.nof_samples_per_buffer = int(samples_per_record)
                return False, 0  # halt status and exit code for setup
            except ValueError:
                return True, 50  # halt status and exit code for setup

    def set_clock_source(self):
        # Set clock source to internal clock
        ADQ_CLK_SOURCE = 0
        clk_set = self.__api.ADQ_SetClockSource(self.__cu, self.device_number, ADQ_CLK_SOURCE)
        if clk_set:
            print('Clock source set to 0 (internal clock)')

    def set_trigger_mode(self, trig_type: str):
        # Get trigger type
        #trigger = TrigMode[trig_type].value
        trig_set = self.__api.ADQ_SetTriggerMode(self.__cu, self.device_number, 2)
        if trig_set:
            print(f"Trigger set to EXTERNAL")
        else:
            print('Failed to set trigger')

    def set_pretrigger(self, samples: int = 0):

        valid = self.__api.ADQ_SetPreTrigSamples(self.__cu, self.device_number, samples)

        if valid:
            print(f"Pretrigger = {samples} samples")
        else:
            print('Failed to set pretrigger')

    def set_trig_delay(self, samples: int = 0):

        valid = self.__api.ADQ_SetTriggerDelay(self.__cu, self.device_number, samples)

        if valid:
            print(f"Trigger delay = {samples} samples")
        else:
            print('Failed to set trigger delay')

    def set_MR_settings(self):
        # Setup SDR-14 for MultiRecord acquisition
        num_records = self.stream_cfg_data.num_of_records
        samples_per_record = self.stream_cfg_data.samples_per_record

        MR_set = self.__api.ADQ_MultiRecordSetup(self.__cu, self.device_number, num_records, samples_per_record)
        if MR_set:
            print('MultiRecord parameters set \n'
                  'Number of records: {}\n'
                  'Samples per record: {}'.format(num_records, samples_per_record))

    def set_external_trig_edge(self):
        valid = self.__api.ADQ_SetExternTrigEdge(self.__cu, self.device_number, 1)

        if valid:
            print(f"External trigger edge set to RISING")
        else:
            print('Failed to set external trigger edge')

    def arm_MR_trigger(self):
        # Deactivate trigger
        self.__api.ADQ_DisarmTrigger(self.__cu, self.device_number)
        # Activate trigger
        trig_armed = self.__api.ADQ_ArmTrigger(self.__cu, self.device_number)
        if trig_armed:
            print('Trigger armed')

    def MR_acquisition(self, trig_mode: str) -> (np.array, np.array):

        # Initialise streaming parameters
        self.set_clock_source()
        # Trigger settings
        self.set_trigger_mode(trig_mode)
        self.set_external_trig_edge()
        # Acquisition settings
        self.set_MR_settings()

        # Arm trigger
        self.arm_MR_trigger()

        # Acquire data
        while self.__api.ADQ_GetAcquiredAll(self.__cu, self.device_number) == 0:
            trig_on = self.__api.ADQ_SWTrig(self.__cu, self.device_number)
            if trig_on:
                print('Trigger activated')
        print('Data acquisition successful')

        # Set up buffers for data
        max_channels = 2
        target_buffers = (ct.POINTER(
            ct.c_int16 * self.stream_cfg_data.samples_per_record * self.stream_cfg_data.num_of_records) * max_channels)()

        for buf_pntr in target_buffers:
            buf_pntr.contents = (
                        ct.c_int16 * self.stream_cfg_data.samples_per_record * self.stream_cfg_data.num_of_records)()

        # Get data from ADQ
        ADQ_TRANSFER_MODE = 0  # Default mode
        ADQ_CHANNELS_MASK = 0x3  # Read from both channels

        status = self.__api.ADQ_GetData(self.__cu, self.device_number, target_buffers,
                                        self.stream_cfg_data.samples_per_record * self.stream_cfg_data.num_of_records,
                                        2, 0, self.stream_cfg_data.num_of_records, ADQ_CHANNELS_MASK,
                                        0, self.stream_cfg_data.samples_per_record, ADQ_TRANSFER_MODE)
        if status:
            print('Data retrieved successfully')

        ch1_data = np.frombuffer(target_buffers[0].contents[0], dtype=np.int16)
        ch2_data = np.frombuffer(target_buffers[1].contents[0], dtype=np.int16)

        # Disarm trigger and close MR mode
        self.__api.ADQ_DisarmTrigger(self.__cu, self.device_number)
        self.__api.ADQ_MultiRecordClose(self.__cu, self.device_number)

        return ch1_data, ch2_data

    def External_MR_acquisition(self, trig_mode: str) -> (np.array, np.array):

        # Initialise streaming parameters
        self.set_clock_source()
        # Trigger settings
        self.set_trigger_mode(trig_mode)
        self.set_external_trig_edge()
        # Acquisition settings
        self.set_MR_settings()

        # Arm trigger
        self.arm_MR_trigger()
        time.sleep(0.1)
        # Acquire data
        self.enable_dev()
        time.sleep(1)
        self.disable_dev()

        """while self.__api.ADQ_GetAcquiredAll(self.__cu, self.device_number) == 0:
            trig_on = self.__api.ADQ_SWTrig(self.__cu, self.device_number)
            if trig_on:
                print('Trigger activated')"""
        print('Data acquisition successful')

        # Set up buffers for data
        max_channels = 2
        target_buffers = (ct.POINTER(
            ct.c_int16 * self.stream_cfg_data.samples_per_record * self.stream_cfg_data.num_of_records) * max_channels)()

        for buf_pntr in target_buffers:
            buf_pntr.contents = (
                        ct.c_int16 * self.stream_cfg_data.samples_per_record * self.stream_cfg_data.num_of_records)()

        # Get data from ADQ
        ADQ_TRANSFER_MODE = 0  # Default mode
        ADQ_CHANNELS_MASK = 0x3  # Read from both channels

        status = self.__api.ADQ_GetData(self.__cu, self.device_number, target_buffers,
                                        self.stream_cfg_data.samples_per_record * self.stream_cfg_data.num_of_records,
                                        2, 0, self.stream_cfg_data.num_of_records, ADQ_CHANNELS_MASK,
                                        0, self.stream_cfg_data.samples_per_record, ADQ_TRANSFER_MODE)
        if status:
            print('Data retrieved successfully')

        ch1_data = np.frombuffer(target_buffers[0].contents[0], dtype=np.int16)
        ch2_data = np.frombuffer(target_buffers[1].contents[0], dtype=np.int16)

        # Disarm trigger and close MR mode
        self.__api.ADQ_DisarmTrigger(self.__cu, self.device_number)
        self.__api.ADQ_MultiRecordClose(self.__cu, self.device_number)

        return ch1_data, ch2_data


    def get_data_setup(self, write_to_file=None, total_records=None, records_per_transfer=None, samples_per_record=None,
                       quiet=None):
        """
        Setup procedure for reading recorded data from SDR14

        Arguments
        ---------
        bool/str: write_to_file (opt) - Write data to file. If True will
                                        use current date/time for file
                                        name. If string, will use string
        int: total_records (opt) - Set total number of records to recieve
        int: records_per_transfer (opt) - Set number of records per
                                          transfer
        int: samples_per_record (opt) - Set samples per record
        bool: quiet (opt) - Override global quiet

        Returns
        -------
            array: data - Data recorded. data[0] = ch1, data[2] = ch2
            int: exit_code - Reason for exit
        """
        quiet = self.__qtest(quiet)

        # initialise streaming parameters
        halt, exit_code = self.stream_cfg_data.set_config(total_records,
                                                          records_per_transfer,
                                                          samples_per_record)
        if exit_code == 50:
            if not quiet:
                print("Config types must be int")
        nof_buffers, nof_samples_per_buffer, sample_skip, \
        bytes_per_sample, clock_source, \
        total_nof_buffers = self.stream_cfg_data.get_config()
        buftype = ct.c_int16 * nof_samples_per_buffer
        filled_buffers = ct.c_uint()
        fetched = 0
        data = [[], []]
        output_file = None

        # Setup device for streaming
        if not self.__api.ADQ_SetClockSource(self.__cu,
                                             self.device_number,
                                             clock_source):
            if not quiet:
                print("Could not set device clock source. Aborting!")
            halt, exit_code = True, 51
        if not self.__api.ADQ_SetTransferBuffers(self.__cu,
                                                 self.device_number,
                                                 nof_buffers,
                                                 nof_samples_per_buffer):
            if not quiet:
                print("Couldn't set transfer buffer configuration. Aborting!")
            halt, exit_code = True, 52
        if not self.__api.ADQ_SetSampleSkip(self.__cu,
                                            self.device_number,
                                            sample_skip):
            if not quiet:
                print("Could not set sample skip rate. Aborting!")
            halt, exit_code = True, 53
        if not self.__api.ADQ_DisarmTrigger(self.__cu,
                                            self.device_number):
            if not quiet:
                print("Could not disarm trigger. Aborting!")
            halt, exit_code = True, 54

        if write_to_file:
            if type(write_to_file) == str:
                output_file = open(write_to_file, "a+")
            else:
                output_file = open(
                    "ADQ-Recording-{:0>2}-{:0>2}-{:0>2}--{:0>2}-{:0>2}-{:0>2}.csv".format(*time.localtime()[0:6]), "a+")

        if not self.__api.ADQ_SetStreamStatus(self.__cu,
                                              self.device_number,
                                              0x1):
            if not quiet:
                print("Could not set stream status. Aborting!")
            halt, exit_code = True, 55

        # Start streaming
        self.stream_cfg_data.tstart = time.time()
        while self.stream_cfg_data.tstart == time.time():
            pass  # wait for timer to progress, prevents div by 0
        if not self.__api.ADQ_StartStreaming(self.__cu,
                                             self.device_number):
            if not quiet:
                print("Could not start streaming data. Aborting!")
            halt, exit_code = True, 60
        try:
            if not quiet and not halt:
                print("\n**************************")
                print("* Staring data recording *")
                print("*          **            *")
                print("*  Press <Ctl-c> at any  *")
                print("*     time to abort      *")
                print("**************************\n")
            while self.stream_cfg_data.records_fetched < total_nof_buffers \
                    and not halt:
                buf, exit_code = self.__fetch_data(buftype,
                                                   output_file,
                                                   exit_code,
                                                   quiet)
                data[0] += buf[0]
                data[1] += buf[1]
            print("")  # newline after record screen data
        except KeyboardInterrupt:
            if not quiet:
                print("Operation cancelled by user")
            exit_code = -1

        if not self.__api.ADQ_StopStreaming(self.__cu,
                                            self.device_number):
            if not quiet:
                print("Could not stop streaming data!")
            exit_code = 61

        if not self.__api.ADQ_SetStreamStatus(self.__cu,
                                              self.device_number,
                                              0x0):
            if not quiet:
                print("Could not disable data stream!")
            exit_code = 62
        return data, exit_code

    def __fetch_data(self, buftype, output_file, exit_code, quiet=None):
        """
        Main loop for fetching a single record set, only to be called with
        correct setup (see get_data_setup)

        Arguments
        ---------
            ctypes array: buftype - Buffer type
            open file/nonetype: output_file - Writeable file (if using)
            int: exit_code - exit code pass through for persistence

        Returns
        -------
            array: data - Data of the form [ch1, ch2]
            int: exit_code - Reason for exit
        """
        ch1 = []
        ch2 = []
        quiet = self.__qtest(quiet)
        filled_buffers = ct.c_uint()
        self.__api.ADQ_GetTransferBufferStatus(self.__cu,
                                               self.device_number,
                                               ct.byref(filled_buffers))
        while filled_buffers.value == 0:
            if not quiet:
                print("\rWaiting for buffers...", end="")
            self.__api.ADQ_GetTransferBufferStatus(self.__cu,
                                                   self.device_number,
                                                   ct.byref(filled_buffers))
        if not quiet:
            recs = self.stream_cfg_data.records_fetched
            # try:
            rate = (recs \
                    * self.stream_cfg_data.nof_samples_per_buffer \
                    * 16) / (time.time() - self.stream_cfg_data.tstart) / 1000000
            # except ZeroDivisionError:
            #    rate = 0.0
            print("\r{: >6} records collected ({:.2f} Mbit/s) -- ".format(recs, rate), end="")
            print("Filled buffers on device: {}/{: <5}".format(filled_buffers.value,
                                                               self.stream_cfg_data.nof_buffers), end="")

        while filled_buffers.value > 0:
            if not self.__api.ADQ_CollectDataNextPage(self.__cu,
                                                      self.device_number):
                if not quiet:
                    print("Failed to fetch record! Data will be incomplete")
                exit_code = 5
            filled_buffers.value -= 1
            self.stream_cfg_data.records_fetched += 1
            if exit_code != 5:
                data_ptr = self.__api.ADQ_GetPtrStream(self.__cu,
                                                       self.device_number)
                data = ct.cast(data_ptr, ct.POINTER(buftype))[0][:]
                lenhalf = int(len(data) / 2)
                ch1 += data[:lenhalf]
                ch2 += data[lenhalf:]
                if output_file:
                    for i in range(lenhalf):
                        output_file.write("{}, {}\n".format(data[i],
                                                            data[lenhalf + i]))
        return [ch1, ch2], exit_code




    ### FOR TESTING ONLY ###


def expand():
    """
    FOR DEVELOPMENT TESTING ONLY.
    """
    sdr14_instance = sdr14()
    api = sdr14_instance._sdr14__api
    cu = sdr14_instance._sdr14__cu
    return sdr14_instance, api, cu


def quick_output_demo(freq):
    """
    Starts the SDR14 with a set of register values to output a signal on
    the output channels and amplifier pulse signal on the GPIO. Deletes
    the control unit immediately.
    """
    dev = sdr14()
    reg = [(1, int(3e6)),
           (2, int(10e3)),
           (3, int(20e3)),
           (5, int(50e3)),
           (7, int(50e3)),
           (0, 1)]
    for i in reg:
        dev.reg_write(*i)
    dev.delete_cu()


def quick_input_demo():
    """
    Starts the SDR14 with a set of register values to output a signal on
    the output channels and amplifier pulse signal on the GPIO. Also
    records a set of data to file (named with the current date and time).
    Deletes the control unit immediately.

    Returns
    -------
        array: data - Collected data of form [ch1, ch2]
    """
    dev = sdr14(quiet=False)
    reg = [(1, int(100e6)),
           (2, int(1)),
           (3, int(500)),
           (5, int(20e3)),
           (7, int(50e3)),
           (0, 1)]
    for i in reg:
        dev.reg_write(*i)
    data = dev.get_data_setup(True)
    dev.delete_cu()
    return data



