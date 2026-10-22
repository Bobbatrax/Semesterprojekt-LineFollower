from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
import time, _thread

### Pins for different things on the board

# motors
motor1 = [0,  1,  2,  3 ]
motor2 = [4,  5,  6,  7 ]
    
# leds
leds =   [16, 17, 18, 19]

# Differential drive object created using both motors
difDrive = DifferentialDrive(motor1+motor2, 0.5, 18000)


# Difdrive move in square
for i in range(4):
    print(i)
    difDrive.move_dist("half", 100, True, 0.005)
    time.sleep_ms(10)
    difDrive.turn_in_place("half", 90, False, 0.005)
    time.sleep_ms(10)




########## older solutions not used for final portfolio solution ##########

### Move in square with _threads ###
#
# for i in range(4):
#     print(i)
#     # Core 1:
#     _thread.start_new_thread(rightMotor.move_dist,("half", 100, True, 0.005))
#     # core 0:
#     leftMotor.move_dist("half", 100, True, 0.005)
#     # Core 1:
#     _thread.start_new_thread(rightMotor.turn_in_place,("half", 90, False, 0.005))
#     # core 0:
#     leftMotor.turn_in_place("half", 89, True, 0.005)
#     time.sleep_ms(5)
###


### Moving using StepperMotor class
#
# # Make a StepperMotor object
# rightMotor = StepperMotor(motor1, 0.6, 18000)
# leftMotor = StepperMotor(motor2, 0.6, 18000)
#
# # Rotate the motor 50 microsteps of size 1/16 fullstep forward
# rightMotor.move(50, "micro", True, 0.001, 16)
#
# # Wait
# time.sleep(1)
# # Rotate the motor with half-steps backwards until the button on the board is pressed
# leftMotor.move_c("half", False, 0.01)
###

##########