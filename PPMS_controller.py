import pyvisa
import numpy as np



class PPMSController:

    def __init__(self):

        # Initialise variables
        self.PPMS = ''
        self.connected = False

        # Try to connect at start
        self.PPMS_connect()

    def PPMS_connect(self):

        try:
            # Set up connection to PPMS
            rm = pyvisa.ResourceManager()
            self.PPMS = rm.open_resource('GPIB0::15::INSTR')
            # Set default read and write termination characters
            self.PPMS.write_termination = ''
            self.PPMS.read_termination = ''
            self.connected = True
        except:
            print('No device found!')




    def test_connection(self):
        pass

    def get_temp(self):
        pass

    def set_temp(self):
        pass

    def set_field(self):
        pass

    def check_helium_level(self):
        pass

    def decode_state(self, state):
        pass


x = PPMSController()