from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
from machine import Pin, ADC, I2C
import time
import gc


# --- Robot ---
left_motor = StepperMotor([0, 1, 2, 3], 0.15, 18000)
right_motor = StepperMotor([4, 5, 6, 7], 0.15, 18000)
difDrive = DifferentialDrive(left_motor, right_motor, 0.15, 18000)
# --- Joystick ---
x_axis = ADC(Pin(27))   # ADC1: turning
y_axis = ADC(Pin(28))   # ADC2: forward / backward
btn = Pin(22, Pin.IN, Pin.PULL_UP)
running = True
# ----Display----

Stick_drift = 2500   # A value that insures that only a diffrence of 2500 makes it move
min_speed, max_speed = 20, 400    # half-steps per second


def interrup(pin):
    global running
    running = False


btn.irq(trigger=Pin.IRQ_FALLING, handler=interrup)

center_x, center_y = 32000, 33823
# average(x_axis), average(y_axis)

# now we define x,y low and high
x_low, x_high = 272, 65535
y_low, y_high = 272, 65503


def axis(raw, center, low, high):
    """Return -1.0 ... +1.0, scaling each side of center separately."""
    offset = raw - center
    # If our offset is smaller than our stick_drift it will return 0.0 and not move
    if abs(offset) < Stick_drift:
        return 0.0
    if offset > 0:  # If our offset is greater 0 then it check how close to 1 then give that amount of power forward
        return min(1.0, (offset - Stick_drift) / (high - center - Stick_drift))
    # If it
    return -min(1.0, (-offset - Stick_drift) / (center - low - Stick_drift))


def clamp(v):
    return max(-1.0, min(1.0, v))
# clamp makes sure that we don't exside +1 or -1. ex. fwd=+0.8 and turn=+0.3   left=(+0.8 + 0.3)=+1.1 clamp makes it (+1)


# Refuse to start if the stick is not near its rest position
# (catches: battery off, joystick unpowered, stick held over)
if (abs(x_axis.read_u16() - center_x) > 5000 or
        abs(y_axis.read_u16() - center_y) > 5000):
    raise SystemExit(
        "Joystick not at rest position. Check power and don't touch the stick.")

# Checks the last steps down to the microsecond
last_step = [time.ticks_us(), time.ticks_us()]
stopped = False  # This makes sure that the motors doesnt stop 10000 time a second

try:
    # I define the list so only the numbers change, and i dont create a new list every time
    speeds = [0.0, 0.0]
    while running:

        # flip sign if backward
        fwd = axis(y_axis.read_u16(), center_y, y_low, y_high)
        # flip sign if reversed
        turn = axis(x_axis.read_u16(), center_x, x_low, x_high)

        # speeds = [clamp(fwd + turn), clamp(fwd - turn)]   # [left, right]
        speeds[0] = clamp(fwd+turn)
        speeds[1] = clamp(fwd-turn)
        speeds
        # if speeds[0] == 0 and speeds[1] == 0:
        #   if not stopped:
        #      difDrive.stop()
        #     stopped = True
        # continue
        # stopped = False
        gc.collect()

        now = time.ticks_us()
        for i in (0, 1):
            s = speeds[i]
            if s == 0:
                continue
            steps_per_sec = min_speed + abs(s) * (max_speed - min_speed)
            interval = int(1_000_000 / steps_per_sec)
            if time.ticks_diff(now, last_step[i]) >= interval:
                last_step[i] = now
                difDrive.step_once(i == 0, 1 if s > 0 else -1)

    difDrive.stop()
except KeyboardInterrupt:
    pass
finally:
    difDrive.stop()
