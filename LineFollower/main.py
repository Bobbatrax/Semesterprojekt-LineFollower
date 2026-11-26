from digital_logger import DigitalSensorLogger
from analog_logger import AnalogSensorLogger
from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
import time
from machine import Timer, Pin

delayLeftMotor = 0.005
delayRightMotor = 0.005

sensor1D = DigitalSensorLogger("GP8","digital_Reading1.csv")
sensor2D = DigitalSensorLogger("GP9","digital_Reading2.csv")


def timerInterrupt(timer):
    global delay
    if sensor1D.sensor.value() == 0:
        delayLeftMotor = 0.005
        #leftMotor.pwm = 0.2
    else:
        delayLeftMotor = 0.01
        #leftMotor.pwm = 0.4

    if sensor2D.sensor.value() == 0:
        delayRightMotor = 0.005
        #leftMotor.pwm = 0.2
    else:
        delayRightMotor = 0.01
        #leftMotor.pwm = 0.4

    #print(sensor1D.sensor.value())
    sensor1D.RAM_storing(timer)
    sensor2D.RAM_storing(timer)

    #sensor1A.RAM_storing(timer)

#Timer interrupts to take a sensor reading
sensor_timer = Timer()
sensor_timer.init(freq=20, mode=Timer.PERIODIC, callback=timerInterrupt)


### Pins for different things on the board

# motors
motor1 = [0,  3,  2,  1 ]
motor2 = [4,  5,  6,  7 ]

leftMotor = StepperMotor(motor2, 0.2, 18_000)


leftMotor.move_c("FULL", True, lambda:delayLeftMotor, duration=30)

#leftMotor.move(20,"FULL",True,0.02)
#difDrive.turn_in_place(sequence="half", angle=280, turn_cw=True, delay=0.005)

#difDrive.turn_in_place(sequence="half", angle=180, turn_cw=False, delay=0.005)

sensor_timer.deinit() #Stops the timer
sensor1D.log_reading() #Writes all the data from the RAM onto a csv-file (should only be done once the robot is done)
sensor2D.log_reading()
#sensor1A.log_reading()