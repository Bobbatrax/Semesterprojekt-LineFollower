from differential_drive import DifferentialDrive
from stepper_motor import StepperMotor
from machine import Pin, ADC
import time

# --- Robot ---
left_motor = StepperMotor([0, 1, 2, 3], 0.2, 18000)
right_motor = StepperMotor([4, 5, 6, 7], 0.2, 18000)
difDrive = DifferentialDrive(left_motor, right_motor, 0.2, 18000)
# --- Joystick ---
x_axis = ADC(Pin(27))   # ADC1: turning
y_axis = ADC(Pin(28))   # ADC2: forward / backward

Stick_drift = 4500
MIN_SPEED, MAX_SPEED = 20, 500    # half-steps per second


def average(adc):
    return sum(adc.read_u16() for _ in range(50)) // 50


# ---- Calibration ----
print("Don't touch the stick...")
time.sleep_ms(1000)
cx, cy = average(x_axis), average(y_axis)
print("rest:", cx, cy)

print("Now move the stick to ALL its limits for 5 seconds!")
x_lo = x_hi = cx
y_lo = y_hi = cy
end = time.ticks_add(time.ticks_ms(), 5000)
while time.ticks_diff(end, time.ticks_ms()) > 0:
    x, y = x_axis.read_u16(), y_axis.read_u16()
    x_lo, x_hi = min(x_lo, x), max(x_hi, x)
    y_lo, y_hi = min(y_lo, y), max(y_hi, y)
    time.sleep_ms(5)
print("X range:", x_lo, cx, x_hi)
print("Y range:", y_lo, cy, y_hi)

# Safety: the stick must have moved a useful amount on both axes, and not be stuck near 0
for name, lo, c, hi in (("X", x_lo, cx, x_hi), ("Y", y_lo, cy, y_hi)):
    if hi - lo < 15000 or hi < 20000 or not (lo + Stick_drift * 2 < c < hi - Stick_drift * 2):
        raise SystemExit(
            f"{name} axis range looks wrong. Check wiring and power, motors not started.")


def axis(raw, center, lo, hi):
    """Return -1.0 ... +1.0, scaling each side of center separately."""
    offset = raw - center
    if abs(offset) < Stick_drift:
        return 0.0
    if offset > 0:
        return min(1.0, (offset - Stick_drift) / (hi - center - Stick_drift))
    return -min(1.0, (-offset - Stick_drift) / (center - lo - Stick_drift))


def clamp(v):
    return max(-1.0, min(1.0, v))


last_step = [time.ticks_us(), time.ticks_us()]
stopped = False

try:
    while True:
        # flip sign if backward
        fwd = axis(y_axis.read_u16(), cy, y_lo, y_hi)
        # flip sign if reversed
        turn = axis(x_axis.read_u16(), cx, x_lo, x_hi)

        speeds = [clamp(fwd + turn), clamp(fwd - turn)]   # [left, right]

        if speeds[0] == 0 and speeds[1] == 0:
            if not stopped:
                difDrive.stop()
                stopped = True
            continue
        stopped = False

        now = time.ticks_us()
        for i in (0, 1):
            s = speeds[i]
            if s == 0:
                continue
            steps_per_sec = MIN_SPEED + abs(s) * (MAX_SPEED - MIN_SPEED)
            interval = int(1_000_000 / steps_per_sec)
            if time.ticks_diff(now, last_step[i]) >= interval:
                last_step[i] = now
                difDrive.step_once(i == 0, 1 if s > 0 else -1)

except KeyboardInterrupt:
    pass
finally:
    difDrive.stop()
