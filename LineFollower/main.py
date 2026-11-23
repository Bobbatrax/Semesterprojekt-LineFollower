from digital_logger import DigitalSensorLogger
from analog_logger import AnalogSensorLogger
from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
import time
from machine import Timer, Pin

#power_pin = Pin("GP22", Pin.OUT)
#power_pin.value(1)

sensor1A = AnalogSensorLogger(0,"digital_Reading1.csv")
sensor1A.clear_log()

sensor2D = DigitalSensorLogger("GP12","digital_Reading2.csv")
sensor2D.clear_log()

#sensor1A = AnalogSensorLogger(0,"analog_Reading.csv")
#sensor1A.clear_log()

def timerInterrupt(timer):
    sensor1A.RAM_storing(timer)
    sensor2D.RAM_storing(timer)

    #sensor1A.RAM_storing(timer)

#Timer interrupts to take a sensor reading
sensor_timer = Timer()
sensor_timer.init(freq=20, mode=Timer.PERIODIC, callback=timerInterrupt)


### Pins for different things on the board

# motors
motor1 = [0,  1,  2,  3 ]
motor2 = [4,  5,  6,  7 ]
noEffectPins = [8, 9, 10, 11]


leftMotor = StepperMotor(pins=motor1, pwm=0.1, frequency=18000)
rightMotor = StepperMotor(pins=motor2, pwm=0.1, frequency=18000)
noEffectMotor = StepperMotor(pins=noEffectPins, pwm=0.1, frequency=18000)

# Differential drive object created using both motors
difDriveLeft = DifferentialDrive(motor1=leftMotor, motor2=noEffectMotor, pwm=0.1, frequency=18000)
difDriveRight = DifferentialDrive(motor1=noEffectMotor, motor2=rightMotor, pwm=0.1, frequency=18000)

difDriveRight.move_dist("full", 100, True, 0.005)
#difDrive.turn_in_place(sequence="half", angle=280, turn_cw=True, delay=0.005)
time.sleep(20)
#difDrive.turn_in_place(sequence="half", angle=180, turn_cw=False, delay=0.005)

sensor_timer.deinit() #Stops the timer
sensor1A.log_reading() #Writes all the data from the RAM onto a csv-file (should only be done once the robot is done)
sensor2D.log_reading()
#sensor1A.log_reading()