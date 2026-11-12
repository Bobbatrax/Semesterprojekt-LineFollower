from machine import Pin, ADC
import time

x_axis = ADC(Pin(26))
y_axis = ADC(Pin(27))
button = Pin(15, Pin.IN, Pin.PULL_UP)

while True:
    x_val = x_axis.read_u16()
    y_val = y_axis.read_u16()
    btn_pressed = button.value() == 0
    print(f"X: {x_val} | Y: {y_val} | Pressed: {btn_pressed}")
    time.sleep(0.1)
