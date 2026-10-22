from stepper_motor import StepperMotor
from machine import Pin, PWM
import time, math


class DifferentialDrive(StepperMotor):
    def __init__(self, pins, pwm=0.15, frequency=18_000):
        """_Class for controlling a robot with two stepper-motors using differential drive control_

        Args:
            pins (list[int]): _output pins for the motor control_. This parameter takes 8 motor pins in a list, the first 4 pins are for controlling motor1 and the last 4 for motor2. Example: [0,1,2,3,4,5,6,7].
            pwm (float): _the fraction of each duty cycle that the power is ON (ON = 1, OFF = 0)._ Defaults to 0.15, meaning "15% ON 75% OFF" in each duty cycle
            frequency (int): _The frequency of the PWM._ Defaults to 18_000 Hertz
        """

        ### Inheretance

        # run the superclass StepperMotor's __init__: sets pins, pwm, frequency,
        # FULL_STEP / HALF_STEP / MICROSTEP and the PWM outputs are also inhereted
        super().__init__(pins, pwm, frequency)

        ### Robot measurements for calculating specific distance and angle stepping
        
        # the distance between each wheel
        self.wheel_base = 24 
        
        # the diameter of the wheels
        self.wheel_dia = 8.6

        # the circumference of the wheels, approximately 27 cm in this case
        self.wheel_cir = math.pi * self.wheel_dia

        # the circumference of the circle found between the wheels, approximately 150,8 cm in this case
        self.turning_cir = 2 * math.pi * self.wheel_base 


    def move_dist(self, sequence, dist, fwd_rot, delay=0.01, microstep_count=0):
        """_Method for moving the robot a specific distance [cm] in either direction_

        Args:
            sequence (string): _motor step sequence_. Options are: "FULL", "HALF", "MICRO". Always converts the string into lowercase.
            dist (int/float): _the distance the robot drives_. Set in cm.
            fwd_rot (bool): driving direction_. Short for "foward rotation", if set to True, the robot drives forward and the other way round for False.
            delay (float, optional): _time (s) between each step_. Defaults to 0.01.
            microsteps (_int_, optional): _amount of microsteps per fullstep_. Defaults to 0, Must be set if sequence is MICRO.
        """

        ### Sequence selection cases

        # full-step
        if sequence.lower() == "full":

            # steps per revolution (per full rotation of the wheel)
            # the motors have a predefined step angle of 1.8* with a full rotation of 200 steps
            steps_per_rev = 360/1.8 # = 200

            # sets the rotation sequence to FULL_STEP a class-variable sequence from the superclass
            sequence = self.FULL_STEP

        elif sequence.lower() == "half":

            # half-step has twice as many steps per rotation, resulting in a step angle half as big, compared to full-step.
            steps_per_rev = 360/(1.8/2) # = 400
            sequence = self.HALF_STEP

        elif sequence.lower() == "micro":

            # for micro-stepping the angle depends on the amount of smaller steps that form one full-step.
            # microstepping with a microstep count of 2 is the same as half-stepping, 
            # you can microstep with any microstep count, but the typical options are: 4, 8, 16, 32, 64, 128, 256 and so on.
            steps_per_rev = 360/(1.8/microstep_count)

            # the microstep sequence is created with a class method from the superclass based on the chosen microstep count
            sequence = self.generate_microstep_sequence(microstep_count)
        else:
            # if an incorrect sequence is chosen it will default to fullstep to avoid errors
            print("Sequence Error, please use of of the listed sequences, defualting to fullstep")
            sequence = self.FULL_STEP

        # the distance travled with a single step
        dist_per_step = self.wheel_cir / steps_per_rev

        # how many steps are required to move the desired distance
        # rounds to the nearest integer
        steps_to_move = round(dist/dist_per_step)

        # amount of steps taken in total
        total_steps = 0
        
        # protect the delay so that it does not become too small for the hardware to handle
        # beware, full-stepping has higher hardware limitation here than half- and microstepping
        if delay < 0.001: delay = 0.001

        # if not rotating forwards, rotate backwards instead
        if not fwd_rot:
            # reversed returns an interator, which is an iterable object with the sequence in reveresed order
            # by typecasting the object into a list, we can operate on it like normal
            sequence = list(reversed(sequence)) 
            step_val = -1
        else:
            step_val = 1

        # try-finally is used to guarantee that the stop() method is always called regardless of any execptions in the try-block
        try:
            # update loop to perform the calculated amount of steps, to move the chosen distance.
            # floor division with the sequence-length is used to reduce the inflated step count to its base value:
            # a single full-step is comprised of 4 smaller steps, for half-step its 8, for micro its even more. 
            # these extra smaller steps are performed in the following for-loop later down.
            for _ in (range(abs(steps_to_move)//len(sequence))):

                # motor coils are updated to the next row in the sequence list (for all rows)
                for step in sequence:

                    # each motor is set to the next sequence row, pwm is updated for all coils
                    self.set_step(step, True)  # True = The left motor
                    self.set_step(step, False) # False = the right motor

                    # wait for the hardware to catch up before continuing
                    time.sleep(delay)

                    # update total steps
                    total_steps += step_val
        finally:
                # turn off all motor coils, stopping all movement
                self.stop()    

                # debugging
                print(f"[move_dist] Total steps performed: {total_steps}")


    def turn_in_place(self, sequence, angle, turn_cw, delay=0.01, microstep_count=0):
        """_Method for rotating (in place) the robot a specific amount of degrees in either direction_

        Args:
            sequence (string): _motor step sequence_. Options are: "FULL", "HALF", "MICRO". Always converts the string into lowercase.
            angle (int/float): _amount of degrees the robot turns_. Angle in degrees e.g. 90 (right-angle turn), 360 (full turn)
            turn_cw (bool): _turning direction_. "Short for turning clockwise" if set to True the robot turn clockwise and the other way round for False.
            delay (float, optional): _time (ms) between each step_. Defaults to 0.01.
            microsteps (_int_, optional): _amount of microsteps per fullstep_. Defaults to 0, Must be set if sequence is MICRO.
        """
        # sequence selection cases
        # see method "move_dist(...)"" for more detailed comment [lines 37-78]
        if sequence.lower() == "full":
            steps_per_rev = 360/1.8
            sequence = self.FULL_STEP
        elif sequence.lower() == "half":
            steps_per_rev = 360/(1.8/2)
            sequence = self.HALF_STEP
        elif sequence.lower() == "micro":
            steps_per_rev = 360/(1.8/microstep_count)
            sequence = self.generate_microstep_sequence(microstep_count)
        else:
            # if an incorrect sequence is chosen it will default to fullstep to avoid errors
            print("Sequence Error, please use of of the listed sequences, defualting to fullstep")
            sequence = self.FULL_STEP

        # the distance travled with a single step
        dist_per_step = self.wheel_cir / steps_per_rev

        # amount of steps to perform a full 360 degree rotation of the robot, using one motor alone
        full_turn = self.turning_cir / dist_per_step

        # how many steps to turn the desired angle, using both motors
        # dividing by 2 because both motors are used and rounding to an int
        steps_to_turn = round((angle/360*full_turn)/2)

        # amount of steps taken in total
        total_steps = 0
        
        # protect the delay so that it does not become too small for the hardware to handle
        if delay < 0.001: delay = 0.001

        # if not turning clockwise, turn counter-clockwise instead
        if turn_cw:
            # reversed returns an interator, which is an iterable object with the sequence in reveresed order
            # by typecasting the object into a list, we can operate on it like normal
            sequence = list(reversed(sequence)) 
            step_val = -1
        else:
            step_val = 1

        # see method "move_dist(...)"" for more detailed comment [lines 103-128]
        try:
            for _ in range(int(abs(steps_to_turn)) // len(sequence)):

                # enumerate creates (yields) an interable object with tuples (tuple: immutable list) with the sequence index and value paired up
                # "i" is the index in the sequence-list, "step" is the value stored in the "i" index of the sequence list
                # e.g i=0 -> step=first step in the sequence
                for i, step in enumerate(sequence):

                    # the left motor
                    self.set_step(step, True)

                    # the right motor 
                    # always goes the oppisite direction of the left motor 
                    # sequence[-1] returns the last step in the sequence 
                    # with sequence[-1 - i] the right motor iterates backwards through the sequence 
                    self.set_step(sequence[-1 - i], False)
                    
                    time.sleep(delay)
                    total_steps += step_val
        finally:
                self.stop()    
                
                # debugging
                print(f"[turn_in_place] Total steps performed: {total_steps}")

            
