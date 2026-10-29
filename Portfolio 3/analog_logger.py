from machine import Pin,ADC
import time



class AnalogSensorLogger:
    def __init__(self,pin,filename="data.csv"):
        self.pin = pin
        self.filename = filename
        self.sensor = ADC(self.pin)
        self.elapsed_time = time.ticks_ms()
        print("yooo" + str(self.elapsed_time))

    def log_reading(self,timer):
        with open(self.filename, "a") as log_file: #Starts file that overwrites the previous one
            
            # Writes the value to the csv-file
            log_file.write(f"{time.ticks_ms()-self.elapsed_time},{self.sensor.read_u16()}\n")
            print(self.sensor.read_u16())

    def clear_log(self):
        with open(self.filename, "w") as log_file:
            pass