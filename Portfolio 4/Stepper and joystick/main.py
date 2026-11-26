from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
from machine import Pin, ADC, SoftI2C
from micropython import const
import time
import _thread
import ssd1306
import gc


# --- Robot ---
left_motor = StepperMotor([0, 1, 2, 3], 0.2, 18000)
right_motor = StepperMotor([4, 5, 6, 7], 0.2, 18000)
difDrive = DifferentialDrive(left_motor, right_motor, 0.2, 18000)
# --- Joystick ---
x_axis = ADC(Pin(27))  # ADC1: turning
y_axis = ADC(Pin(28))  # ADC2: forward/backward
btn = Pin(22, Pin.IN, Pin.PULL_UP)
running = True
# ----Display----
i2c = SoftI2C(scl=Pin(21), sda=Pin(20))

WIDTH = const(128)
HEIGHT = const(64)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)


def display_task():
    last = (None, None)
    while running:
        gc.collect()
        L = round(int(speeds[0] * 100))
        R = round(int(speeds[1] * 100))
        if (L, R) != last:
            oled.fill(0)
            oled.text("Left:  %d%%" % L, 0, 0)
            oled.text("Right: %d%%" % R, 0, 16)
            oled.show()
            last = (L, R)
        time.sleep_ms(50)   # always yield, whether or not the display changed


Stick_drift = 3500   # A value that insures that only a diffrence of 3500 makes it move
min_speed, max_speed = 20, 200    # Full-steps per second

# I define the list so only the numbers change, and i dont create a new list every timeFs
speeds = [0.0, 0.0]


def interrup(pin):
    global running
    running = False


btn.irq(trigger=Pin.IRQ_FALLING, handler=interrup)

center_x, center_y = 32000, 33823
# average(x_axis), average(y_axis)

# now we define x,y low and high
x_low, x_high = 272, 65500
y_low, y_high = 272, 65500


def axis(raw, center, low, high):
    """Return -1.0 ... +1.0, scaling each side of center separately."""
    offset = raw - center
    # If our offset is smaller than our stick_drift it will return 0.0 and not move
    if abs(offset) < Stick_drift:
        return 0.0
    if offset > 0:  # If our offset is greater 0 then it check how close to 1 then give that amount of power forward
        # Negative direction: -offset makes the distance positive, and Stick_drift is subtracted from both numerator and denominator so the output scales
        # smoothly from 0.0 at the stickdrift edge to -1.0 at the low limit. min(1.0, ...) clips if raw < low.
        return min(1.0, (offset - Stick_drift) / (high - center - Stick_drift))
        # Same as the positive branch, but mirrored: -offset makes the distance positive, and the result is negated at the end
    return -min(1.0, (-offset - Stick_drift) / (center - low - Stick_drift))


def clamp(v):
    return max(-1.0, min(1.0, v))
# clamp makes sure that we don't exside -1 or +1. ex. fwd=+0.8 and turn=+0.3   Motor2=(+0.8 + 0.3)=+1.1 clamp makes it (+1)


# Refuse to start if the stick is not near its rest position ex. if battry is off or cables in joystick aren't connected
if (abs(x_axis.read_u16() - center_x) > 5000 or
        abs(y_axis.read_u16() - center_y) > 5000):
    raise SystemExit(
        "Joystick not at rest position. Check power and don't touch the stick.")


# Checks the last steps down to the microsecond
last_step = [time.ticks_us(), time.ticks_us()]

_thread.start_new_thread(display_task, ())
try:

    while running:

        # This read y_axis and the axis function makes it a float between -1 (Fully backwards) and +1(Fully forwards)
        # it subtracs the center from the raw imput to get the offset. then scales each side og the center separatly
        fwd = axis(y_axis.read_u16(), center_y, y_low, y_high)
        # Does the same for the x_axis   -1(full left) and +1 (full right)
        turn = axis(x_axis.read_u16(), center_x, x_low, x_high)

        # We call speeds[] since speeds is shared with display.thread
        speeds[0] = clamp(fwd+turn)
        # clamp(fwd + turn), clamp(fwd - turn)]   (left motor, right motor)
        # + is used for left and - for right. If we need to turn right we add speed to the left wheel and sub speed from the right
        speeds[1] = clamp(fwd-turn)
        # now is used to capture the time so both motors can compare against the same now
        now = time.ticks_us()

        for i in (0, 1):
            # for i in we use a tuble (0,1), since it iterates over both motors i=0 left i=1 right
            s = speeds[i]
            # grabs the current speed fraction (-1.0 ... +1.0) the sign is direction and abs value is how fast
            if s == 0:
                # if the speed is 0, skip the timing calculations for the non moving motor(s)
                continue
            steps_per_sec = min_speed + abs(s) * (max_speed - min_speed)
            # This maps the speed fraction to a step frequency in steps_per_sec
            interval = int(1_000_000 / steps_per_sec)
            # Converts freq into a period
            if time.ticks_diff(now, last_step[i]) >= interval:
                # checks if enough time has passed since the last step
                last_step[i] = now
                # sends the time, when we step
                difDrive.step_once(i == 0, 1 if s > 0 else -1)
                # Makes the motors step, by turning and int to a bool, and converts the sign of s into +1 or -1

    difDrive.stop()
    # stops the motors
except KeyboardInterrupt:
    pass
finally:
    running = False
    time.sleep_ms(400)
    difDrive.stop()
