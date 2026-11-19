from machine import Pin, I2C
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)
for i in range(10):
    try:
        i2c.writeto(0x3C, bytes([0x80, 0xAE]))   # "display off" command
        print(i, "ok")
    except OSError as e:
        print(i, "fail", e)
    print(i2c.scan())
