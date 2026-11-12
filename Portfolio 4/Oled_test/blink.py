from machine import Pin, I2C
import ssd1306
import machine
import time
import wifi_sender

led = machine.Pin("LED", machine.Pin.OUT)


def blink(timer):
    led.toggle()


timer = machine.Timer()
timer.init(freq=1, mode=machine.Timer.PERIODIC, callback=blink)

adcpin = 4
sensor = machine.ADC(adcpin)
meter = machine.ADC(26)


def Potensmeter():
    meter_value = meter.read_u16()
    procent = meter_value * 100 / 65535
    return round(procent, 1)


def ReadTemperature():
    adc_value = sensor.read_u16()
    volt = (3.3/65535) * adc_value
    temperature = 27 - (volt - 0.706)/0.001721
    time.sleep(1)
    return round(temperature, 1)


def count(number):
    return number + 1


i2c = machine.I2C(0, sda=machine.Pin(8), scl=machine.Pin(9)
                  )  # EIO error almost immediately
# i2c = machine.I2C(1, sda=machine.Pin(10), scl=machine.Pin(11))  # EIO error almost immediately

i2c_dev = i2c.scan()  # scan for devices
print(i2c_dev)

# using default address 0x3C
display = ssd1306.SSD1306_I2C(128, 64, i2c)
number = 0
counter = 0
slow = 100
remote = "--"
last_fetch = time.ticks_ms()
temp = ReadTemperature()
try:
    while True:
        if counter % slow == 0:
            temp = ReadTemperature()
        number = count(number)
        per = Potensmeter()

    # fetch remote temp every 2 seconds
        if time.ticks_diff(time.ticks_ms(), last_fetch) > 2000:
            value = wifi_sender.get_remote_temp()
            remote = value if value is not None else "ERR"
            last_fetch = time.ticks_ms()

        display.fill(0)
        display.text('Temp: ' + str(temp), 0, 0, 1)
        display.text('Power:' + str(per) + '%', 0, 12, 1)
        display.text('Count: ' + str(number), 0, 24, 1)
        display.text('Remote:' + remote, 0, 36, 1)
        display.show()
        counter += 1
        time.sleep_ms(1)
finally:
    display.poweroff()
