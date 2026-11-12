from machine import Pin,Timer
import time



class DigitalSensorLogger:
    def __init__(self,pin,filename="data.csv"):
        self.pin = pin
        self.filename = filename
        self.sensor = Pin(self.pin, Pin.IN)
        self.elapsed_time = time.ticks_ms()
        self.readings = []
        print("yooo" + str(self.elapsed_time))

    def RAM_storing(self,timer): #While the robot is moving, the data will only be stored on the RAM, because that is much faster
        print(self.sensor.value())
        self.readings.append(f"{time.ticks_ms()-self.elapsed_time},{self.sensor.value()}")

    #After the robot is done moving, all the data can be writting onto a file.
    def log_reading(self): #Note timer is not an actual parameter, just a quirk of the timer function
        with open(self.filename, "a") as log_file: #Starts file that overwrites the previous one
            
            # Writes the value to the csv-file
            for i in range(len(self.readings)):
                log_file.write(f"{self.readings[i]}\n")
                print(self.sensor.value())

    def clear_log(self):
        with open(self.filename, "w") as log_file:
            pass