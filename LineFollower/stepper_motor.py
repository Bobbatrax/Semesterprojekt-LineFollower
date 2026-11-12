# Portfolio 2: Differential Drive Class
# built around Extra Credit Activity 2: Stepper Motor Controller
# finished date: 22/10/2026

from machine import Pin, PWM
import time, math

class StepperMotor:
    def __init__(self, pins, pwm=0.15, frequency=18_000):
        """_Class for controlling a Stepper Motor, Serves as a Superclass_

        Args:
            pins (list[int]): _output pins for the motor control_
            pwm (float): _the fraction of each duty cycle that the power is ON (ON = 1, OFF = 0)._ Defaults to 0.15, meaning "15% ON 75% OFF" in each duty cycle
            frequency (int): _The frequency of the PWM._ Defaults to 18_000 hertz
        """

        # rename the pins to match the GPIO pin syntax
        self.pins = [f"GP{p}" for p in pins]

        # turn the pins into PWM objects usable by the motors
        self.outputs = [PWM(Pin(p, Pin.OUT)) for p in self.pins]

        # the max pwm fraction
        # full-step and half-step both default to using max pwm, while micro-step uses from 0-max pwm
        self.pwm = pwm 

        # frequency is the PWM frequency in hertz
        self.frequency = frequency 


        ### Full and Half-step sequenceses, based on the max pwm of the motor

        # one step per coil, by updating 2 coils at a time
        self.FULL_STEP = [
            [self.pwm, self.pwm, 0       , 0       ],  # Step 0
            [0       , self.pwm, self.pwm, 0       ],  # Step 1
            [0       , 0       , self.pwm, self.pwm],  # Step 2
            [self.pwm, 0       , 0       , self.pwm],  # Step 3
        ]

        # twice as many steps as Fullstep, by only updating 1 coil at a time
        self.HALF_STEP = [
            [self.pwm, 0       , 0       , 0       ],  # Step 0
            [self.pwm, self.pwm, 0       , 0       ],  # Step 1
            [0       , self.pwm, 0       , 0       ],
            [0       , self.pwm, self.pwm, 0       ],
            [0       , 0       , self.pwm, 0       ],
            [0       , 0       , self.pwm, self.pwm],
            [0       , 0       , 0       , self.pwm],  
            [self.pwm, 0       , 0       , self.pwm],  # Step 7
        ]

        # set the pwm frequency of all output pins
        for output in self.outputs:
            output.freq(self.frequency)

    def set_step(self, step):
        """_Apply a step to the selected PWM outputs._"""
        for output, duty_cycle in zip(self.outputs, step):
            output.duty_u16(int(duty_cycle * 65535))

    def stop(self):
        """_Set the PWM duty cycle of all outputs to zero._"""
        # turns off all coils from both motors, by setting their pwm to 0
        self.set_step([0, 0, 0, 0])

        
    def generate_microstep_sequence(self, microsteps):
        """_Method for generating a microstep-sequence_

        Args:
            microsteps (_int_): _how many microsteps per fullstep_

        Returns:
            sequence (_list_): _a functional microstep sequence for motor control_
        """
        # empty list that will be filled with rows: [a, b, c, d]
        sequence = []

        # outer loop for all the four coils
        for coil in range(4):

            # inner loop for each microstep (for each coil)
            for i in range(microsteps):

                # the angle: between 0* and 90* (pi/2=90*)
                # as i increases the angle increases to reach 90*
                angle = (math.pi / 2) * i / microsteps 

                # creates an empty row with all 4 couls turned off 
                row = [0.0] * 4
                
                # the value pwm/duty cycle of first coil based of the angle
                # as the angle increases from 0* to 90* the first coil will power down
                row[coil] = round(self.pwm * math.cos(angle), 4)

                # while the next coil will power up along side it
                row[(coil + 1) % 4] = round(self.pwm * math.sin(angle), 4)

                # each row is then saven in the sequence list
                sequence.append(row)

        # the completed sequence is completed and returned.
        return sequence

    # regular rotation
    def move(self, steps: int, sequence, fwd_rot = True, delay = 0.001, microsteps=None):
        """_Method for rotating a stepper motor a set amount of steps._

        Args:
            steps (int): _steps the motor will rotate_.
            sequence (string): _motor step sequence_. Options are: "FULL", "HALF", "MICRO". Always converts the string into lowercase.
            fwd_rot (bool): driving direction_. Short for "foward rotation", if set to True, the robot drives forward and the other way round for False.
            delay (float, optional): _time (s) between each step_. Defaults to 0.001.
            microsteps (_int_, optional): _amount of microsteps per fullstep_. Defaults to None, Must be set if sequence is MICRO.
        """
        ### sequence selection cases
        if sequence.lower() == "full":
            sequence = self.FULL_STEP   # sets the rotation sequence to FULL_STEP

        elif sequence.lower() == "half":
            sequence = self.HALF_STEP   # sets the rotation sequence to HALF_STEP

        elif sequence.lower() == "micro":
            sequence = self.generate_microstep_sequence(microsteps) # the microstep sequence is created

        else:
            # if an incorrect sequence is chosen it will default to fullstep to avoid errors
            print("Sequence Error, please use of of the listed sequences, defualting to fullstep")
            sequence=self.FULL_STEP

        # amount of steps taken in total
        total_steps = 0
        
        # protect the delay so that it does not become too small for the hardware to handle
        if delay < 0.001: delay = 0.001

        # if not rotation forwards, rotate backwards instead
        if not fwd_rot:

            # reversed returns an interator, which is an iterable object with the sequence in reveresed order
            # by typecasting the object into a list we can operate on it like normal
            sequence = list(reversed(sequence)) 
            step_val = -1
        else:
            step_val = 1

        # try-finally is used to garantee that the stop method is always called regardless of any execptions in the try-block
        try:
            # the entire sequence is 1 step
            for _ in (range(abs(steps))):
                # motor coils are updated to the next row in the sequence list (for all rows)
                for step in sequence:
                    self.set_step(step) # true = left motor

                    # wait for the hardware to catch up
                    time.sleep(delay)

                    # update total steps
                    total_steps += step_val
        finally:
                # turn off all coils, stop moving
                self.stop()       

        # debugging
        print(total_steps)  


    # continuous rotation stopped by onboard button
    def move_c(self, sequence, fwd_rot = True, delay = 0.001, microsteps=None, stop_btn = Pin(27, Pin.IN, Pin.PULL_UP)):
        """_Method for rotating a steppermotor continously until a button interupts it._

        Args:
            sequence (string): _motor step sequence_. Options are: "FULL", "HALF", "MICRO". Always converts the string into lowercase.
            fwd_rot (bool): driving direction_. Short for "foward rotation", if set to True, the robot drives forward and the other way round for False.
            delay (float, optional): _time (s) between each step_. Defaults to 0.001.
            microsteps (_int_, optional): _amount of microsteps per fullstep_. Defaults to None, Must be set if sequence is MICRO.
            stop_btn (_Pin_, optional): _button for stopping motor rotation_. Defaults to the onboard btn pin: Pin(27, Pin.IN, Pin.PULL_UP).
        """
        ### sequence selection cases
        if sequence.lower() == "full":
            sequence = self.FULL_STEP   # sets the rotation sequence to FULL_STEP

        elif sequence.lower() == "half":
            sequence = self.HALF_STEP   # sets the rotation sequence to HALF_STEP

        elif sequence.lower() == "micro":
            sequence = self.generate_microstep_sequence(microsteps) # the microstep sequence is created

        else:
            # if an incorrect sequence is chosen it will default to fullstep to avoid errors
            print("Sequence Error, please use of of the listed sequences, defualting to fullstep")
            sequence=self.FULL_STEP

        # vars
        total_steps = 0
        running = True
        step_val = 1
        if delay < 0.001: delay = 0.001

        # direction
        if not fwd_rot:
            sequence = list(reversed(sequence))
            step_val = -1

        # continuous loop
        while running:

            # keep the loop running until the button is pressed
            # 1 and 0 are button-states where 0 is pressed and 1 is not
            if stop_btn.value() == 0:

                # stop the loop
                running = False

                # turn of all 4 coils on the motor
                self.stop()

            else:
                
                # motor coils are updated to the next row in the sequence list (for all rows)
                for step in sequence:
                    self.set_step(step)
                    time.sleep(delay)
                    total_steps += step_val

        # debugging
        print(total_steps)