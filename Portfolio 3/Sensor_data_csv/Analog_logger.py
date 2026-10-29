from machine import Pin,ADC
import time



class AnalogSensorLogger:
    def __init__(self,pin):
        self.pin = pin
        self.sensor = ADC(self.pin)

    def log_reading(self,filename="data.csv"):
        with open(filename, "w") as log_file: #Starts file that overwrites the previous one
            t = time.localtime() # The pico's local time starts when powered on

            # timestamp starts at: 2021-01-01 00:00:00
            timestamp = f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}" 
            
            # Writes the value to the csv-file
            log_file.write(f"{timestamp},{self.sensor.read_u16()}\n")
sensor1 = SensorLogger(0)
sensor1.log_reading()