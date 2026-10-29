from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
import time

### Pins for different things on the board

# motors
motor1 = [0,  1,  2,  3 ]
motor2 = [4,  5,  6,  7 ]


leftMotor = StepperMotor(pins=motor1, pwm=0.5, frequency=18000)
rightMotor = StepperMotor(pins=motor2, pwm=0.5, frequency=18000)


# Differential drive object created using both motors
difDrive = DifferentialDrive(motor1=leftMotor, motor2=rightMotor, pwm=0.5, frequency=18000)