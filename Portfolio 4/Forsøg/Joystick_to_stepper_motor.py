from machine import Pin, PWM, ADC
import time


motor_pins = [0, 1, 2, 3]
PWM_freq = 20000
duty = 4000
Center = 32768
sd = 4000
min_speed, max_speed = 1, 15

seq = [
    (1, 0, 1, 0),
    (0, 1, 1, 0),
    (0, 1, 0, 1),
    (1, 0, 0, 1),
]

pwms = []
for gp in motor_pins:
    p = PWM(Pin(gp))
    p.freq(PWM_freq)
    p.duty_u16(0)
    pwms.append(p)

x_axis = ADC(Pin(26))
y_axis = ADC(Pin(27))
Button = Pin(22, Pin.IN, Pin.PULL_UP)


def set_step(i):
    for p, on in zip(pwms, seq[i]):
        p.duty_u16(min(duty, 13107) if on else 0)


def release():
    for p in pwms:
        p.duty_u16(0)


step_index = 0
last_step = time.ticks_us()

try:
    while True:
        offset = x_axis.read_u16()-Center
        print(x_axis.read_u16(), y_axis.read_u16())
        if abs(offset) > sd:
            frac = min(1.0, (abs(offset)-sd)/(Center-sd))
            speed = min_speed+frac*(max_speed-min_speed)
            interval = int(1_000_000/speed)

            if time.ticks_diff(time.ticks_us(), last_step) >= interval:
                last_step = time.ticks_us()
                step_index = (step_index + (1 if offset > 0 else -1)) % 4
                set_step(step_index)
        else:
            release()

except KeyboardInterrupt:
    release()
    for p in pwms:
        p.deinit()
