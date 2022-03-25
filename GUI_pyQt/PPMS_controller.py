import pyvisa
import numpy as np
import time

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
            print('No PPMS found!')
            self.connected = False

    def test_connection(self):
        pass

    def get_temp(self):
        pass

    def set_temp(self, set_point, rate):

        # Test connection

        if self.connected:

            # Write GPIB command
            self.PPMS.write(f'TEMP {str(set_point)} {str(rate)} 0')

            # Measure

            temp_status = 0
            while temp_status != 1:

                # Get temp info and print
                temp_info = self.PPMS.query('GetDat? 2')
                t = temp_info.split(',')[1]
                T = temp_info.split(',')[2][:-1]

                print()
                print(f'Timestamp: {t}s')
                print(f'Temperature: {T}K')
                print()

                # Check temp state

                system_status = self.PPMS.query('GetDat? 1')
                system_state = int(system_status.split(',')[-1][:-1])
                temp_status, field_status = self.decode_state(system_state)
                print(f'Temp status = {temp_status}')

                time.sleep(2)

            print(f'Temperature stabilised at {set_point}K')


    def set_field(self, set_point, rate):
        # Test connection

        if self.connected:

            # Write GPIB command
            self.PPMS.write(f'FIELD {str(set_point)} {str(rate)} 0')

            # Measure

            field_status = 0
            while field_status != 1:
                # Get field info and print
                temp_info = self.PPMS.query('GetDat? 4')
                t = temp_info.split(',')[1]
                B = temp_info.split(',')[2][:-1]

                print()
                print(f'Timestamp: {t}s')
                print(f'Magnetic Field: {B}Oe')
                print()

                # Check field state
                system_status = self.PPMS.query('GetDat? 1')
                system_state = int(system_status.split(',')[-1][:-1])
                temp_status, field_status = self.decode_state(system_state)
                print(f'Field status = {temp_status}')

                time.sleep(2)

            print(f'Field stabilised at {set_point} Oe')

    def check_helium_level(self):
        pass

    @staticmethod
    def decode_state(self, state):

        state_binary = f'{state:016b}'

        temp_state = state_binary[12:16]
        field_state = state_binary[8:12]
        chamber_state = state_binary[4:8]
        pos_state = state_binary[0:4]

        temp_state_dec = int(temp_state, 2)
        field_state_dec = int(field_state, 2)

        return temp_state_dec, field_state_dec


x = PPMSController()