from machine import Pin, I2C
import ssd1306
import machine
import time

adc_temp = machine.ADC(4)
meter = machine.ADC(26)


def Potensmeter():
    return round(meter.read_u16() * 100 / 65535, 1)


def ReadTemperature():
    volt = (3.3 / 65535) * adc_temp.read_u16()
    return round(27 - (volt - 0.706) / 0.001721, 1)


i2c = machine.I2C(0, sda=machine.Pin(8), scl=machine.Pin(9))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

x = 128  # start just off the right edge

while True:
    temp = ReadTemperature()
    per = Potensmeter()

    message = "Temp: " + str(temp) + " C   Power: " + str(per) + "%"
    text_width = len(message) * 8

    display.fill(0)
    display.text(message, x, 28, 1)  # scrolling line
    display.text("Static line", 0, 0, 1)  # stays in place
    display.show()

    x -= 2                    # speed: pixels per frame
    if x < -text_width:       # fully off the left edge
        x = 128               # restart from the right

    time.sleep(0.03)
