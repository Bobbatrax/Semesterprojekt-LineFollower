from analog_logger import AnalogSensorLogger
from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
import time
from machine import Timer, Pin

#power_pin = Pin("GP22", Pin.OUT)
#power_pin.value(1)

sensor1 = AnalogSensorLogger(pin=0)
sensor1.clear_log()

Timer().init(freq=100, mode=Timer.PERIODIC, callback=sensor1.log_reading)

### Pins for different things on the board

# motors
motor1 = [0,  1,  2,  3 ]
motor2 = [4,  5,  6,  7 ]


leftMotor = StepperMotor(pins=motor1, pwm=0.5, frequency=18000)
rightMotor = StepperMotor(pins=motor2, pwm=0.5, frequency=18000)


# Differential drive object created using both motors
difDrive = DifferentialDrive(motor1=leftMotor, motor2=rightMotor, pwm=0.5, frequency=18000)

#difDrive.turn_in_place(sequence="half", angle=180, turn_cw=True, delay=0.005)