import pyvisa
import time
import numpy as np


class PPMS:

    def __init__(self) -> None:
        self.rm = pyvisa.ResourceManager()
        self.ppms = self.rm.open_resource("GPIB0::15::INSTR")
        """
        try:
            self.ppms = self.rm.open_resource("GPIB0::15::INSTR")
            self.ppms.write_termination = ""
            self.ppms.read_termination = ""
       except:
            print("No device found")"""


    def get_current_conditions(self) -> [float, float]:
        return self.get_temperature, self.get_field

    def set_temperature(self, set_temp: float, rate: float) -> None:

        self.ppms.write(f"TEMP {set_temp} {rate} 0")

        # Log temperature as function of time
        timestamps = []
        temp = []
        state = []

        # Measure
        temp_status = 0
        while temp_status != 1:
            # Get temp info and print
            temp_info = PPMS.query("GetDat? 2")
            t = temp_info.split(",")[1]
            T = temp_info.split(",")[2][:-1]

            print()
            print(f"Timestamp: {t}s")
            print(f"Temperature: {T}K")
            print()

            # Check temp state
            system_status = PPMS.query("GetDat? 1")
            system_state = int(system_status.split(",")[-1][:-1])
            temp_status = decode_state(system_state)['temp']
            print(f"Temp status = {temp_status}")

            timestamps.append(t)
            temp.append(T)
            state.append(temp_status)

            time.sleep(2)

        print(f"Temperature stabilised at {set_temp}")

    def get_temperature(self) -> float:

        temp_info = PPMS.query("GetDat? 2")
        T = float(temp_info.split(",")[2][:-1])

        return T

    def set_field(self, set_field: float, rate: float) -> None:

        # Log field as function of time
        timestamps = []
        field = []
        state = []

        # Measure
        field_status = 0
        while field_status != 1:
            # Get temp info and print
            field_info = PPMS.query("GetDat? 4")
            t = field_info.split(",")[1]
            H = field_info.split(",")[2][:-1]

            print()
            print(f"Timestamp: {t}s")
            print(f"Field: {T}Oe")
            print()

            # Check field state
            system_status = PPMS.query("GetDat? 1")
            system_state = int(system_status.split(",")[-1][:-1])
            field_status = decode_state(system_state)['field']
            print(f"Field status = {field_status}")

            timestamps.append(t)
            field.append(H)
            state.append(field_status)

            time.sleep(2)

        print(f"Field stabilised at {set_field}")

    def get_field(self) -> float:
        field_info = PPMS.query("GetDat? 4")
        H = float(field_info.split(",")[2][:-1])

        return H


    @staticmethod
    def decode_state(state: int) -> dict[str:int]:

        state_binary = f"{state:016b}"

        temp_state = int(state_binary[12:16], 2)
        field_state = int(state_binary[8:12], 2)
        chamber_state = int(state_binary[4:8], 2)
        position_state = int(state_binary[0:4], 2)

        return {'temp': temp_state, 'field': field_state, 'chamber': chamber_state, 'position': position_state}


x = PPMS()
