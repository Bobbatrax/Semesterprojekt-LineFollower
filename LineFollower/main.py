from digital_logger import AnalogSensorLogger
from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
import time
from machine import Timer, Pin

#power_pin = Pin("GP22", Pin.OUT)
#power_pin.value(1)

sensor1 = DigitalSensorLogger("GP8")
sensor1.clear_log()

#Timer interrupts to take a sensor reading
sensor_timer = Timer()
sensor_timer.init(freq=20, mode=Timer.PERIODIC, callback=sensor1.RAM_storing)
time.sleep(2)

sensor_timer.deinit() #Stops the timer
sensor1.log_reading() #Writes all the data from the RAM onto a csv-file (should only be done once the robot is done)

### Pins for different things on the board

# motors
motor1 = [0,  1,  2,  3 ]
motor2 = [4,  5,  6,  7 ]


leftMotor = StepperMotor(pins=motor1, pwm=0.1, frequency=18000)
rightMotor = StepperMotor(pins=motor2, pwm=0.1, frequency=18000)


# Differential drive object created using both motors
difDrive = DifferentialDrive(motor1=leftMotor, motor2=rightMotor, pwm=0.1, frequency=18000)