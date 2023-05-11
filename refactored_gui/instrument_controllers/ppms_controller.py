import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt


class PPMS_GPIB:

    def __init__(self, debug_mode: bool = False) -> None:
        self.debug_mode = debug_mode
        self.rm = pyvisa.ResourceManager()
        self.ppms = self.rm.open_resource("GPIB0::15::INSTR")
        self.ppms.write_termination = ""
        self.ppms.read_termination = ""


            
    def get_current_conditions(self) -> [float, float]:
        return self.get_temperature(), self.get_field()

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
            temp_info = self.ppms.query("GetDat? 2")
            t = temp_info.split(",")[1]
            T = temp_info.split(",")[2][:-1]

            print()
            print(f"Timestamp: {t}s")
            print(f"Temperature: {T}K")
            print()

            # Check temp state
            system_status = self.ppms.query("GetDat? 1")
            system_state = int(system_status.split(",")[-1][:-1])
            temp_status = self.decode_state(system_state)['temp']
            print(f"Temp status = {temp_status}")

            timestamps.append(t)
            temp.append(T)
            state.append(temp_status)

            time.sleep(1)

        print(f"Temperature stabilised at {set_temp}")
        
        if self.debug_mode:
            
            timestamps = np.array(timestamps)
            temp = np.round(np.array(temp), 3)
            
            
            plt.figure()
            plt.plot(timestamps - timestamps[0], temp)
            plt.title("T as function of time")
            plt.xlabel("Time (s)")
            plt.ylabel("T (K)")
            
            plt.figure()
            plt.plot(timestamps - timestamps[0], state)
            plt.title("Temperature status as function of time")
            plt.xlabel("Time (s)")
            plt.ylabel("Temperature status")
        

    def get_temperature(self) -> float:

        temp_info = self.ppms.query("GetDat? 2")
        T = float(temp_info.split(",")[2][:-1])

        return T
    

    def set_field(self, set_field: float, rate: float) -> None:
        
        time.sleep(10)
        self.ppms.write(f"FIELD {set_field} {rate}")
        
        
        for i in range(10):
            
            
            system_status = self.ppms.query("GetDat? 1")
            system_state = int(system_status.split(",")[-1][:-1])
            self.decode_state(system_state)
            
            time.sleep(1)
        
        
        #time.sleep(20)
        #print(self.ppms.query("GETDAT? 4"))
        
        """# Log field as function of time
        timestamps = []
        field = []
        state = []

        # Measure
        field_status = 0
        i = 0
        while i < 10:
            # Get temp info and print
            field_info = self.ppms.query("GetDat? 4")
            t = field_info.split(",")[1]
            H = field_info.split(",")[2][:-1]

            print()
            print(f"Timestamp: {t}s")
            print(f"Field: {H}Oe")
            print()

            # Check field state
            system_status = self.ppms.query("GetDat? 1")
            system_state = int(system_status.split(",")[-1][:-1])
            field_status = self.decode_state(system_state)['field']
            print(f"Field status = {field_status}")

            timestamps.append(t)
            field.append(H)
            state.append(field_status)

            time.sleep(3)
            i += 1

        print(f"Field stabilised at {set_field}Oe")
        
        
        if self.debug_mode:
            plt.figure()
            plt.plot(timestamps, field)
            plt.title("H as function of time")
            plt.xlabel("Time (s)")
            plt.ylabel("H (Oe)")
            
            plt.figure()
            plt.plot(timestamps, state)
            plt.title("Field status as function of time")
            plt.xlabel("Time (s)")
            plt.ylabel("Field status")"""
        

    def get_field(self) -> float:
        field_info = self.ppms.query("GetDat? 4")
        H = float(field_info.split(",")[2][:-1])

        return H


    
    def decode_state(self, state: int) -> dict[str:int]:

        state_binary = f"{state:016b}"


        temp_state = int(state_binary[12:16], 2)
        field_state = int(state_binary[8:12], 2)
        chamber_state = int(state_binary[4:8], 2)
        position_state = int(state_binary[0:4], 2)
        
        if self.debug_mode:
            print({'temp': temp_state, 'field': field_state, 'chamber': chamber_state, 'position': position_state})

        return {'temp': temp_state, 'field': field_state, 'chamber': chamber_state, 'position': position_state}


class PPMS_MultiPyVu:
    
    def __init__(self):
        pass
    
    
    
