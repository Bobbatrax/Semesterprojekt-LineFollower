from stepper_motor import StepperMotor
import time, _thread

# Pins for different things on the board
    # motors
motor1 = [0,  1,  2,  3 ]
motor2 = [4,  5,  6,  7 ]
    # leds
leds =   [16, 17, 18, 19]

# Make a StepperMotor object
rightMotor = StepperMotor(motor1, 0.5, 18000)
leftMotor = StepperMotor(motor2, 0.5, 18000)


# Rotate the motor 50 microsteps of size 1/16 fullstep forward
#rightMotor.move(50, "micro", True, 0.001, 16)



# Wait
#time.sleep(1)
# Rotate the motor with half-steps backwards until the button on the board is pressed
#leftMotor.move_c("half", False, 0.01)

# Update loop using threads

# Core 1:
_thread.start_new_thread(rightMotor.move,(50, "full", True, 0.01))
# core 0:
leftMotor.move(50, "full", True, 0.01)