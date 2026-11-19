from machine import Pin, PWM, ADC
import time

# Initialize PWM on GP0 with a 50Hz frequency (standard for hobby servos)
servo = PWM(Pin(0))
servo.freq(50)

x_axis = ADC(Pin(26))
y_axis = ADC(Pin(27))
button = Pin(15, Pin.IN, Pin.PULL_UP)
# Joystick


def read_axis():
    x_val = x_axis.read_u16()
    y_val = y_axis.read_u16()

    # print(x_val, y_val, 0, 70000)
    return x_val, y_val


in_min, in_max = 800, 65535  # Joystick min and max input
duty_min, duty_max = 1802, 7864  # Servo min and max output
Stick_drift = 100  # If the movement is under 100 it dont move
last_x = None  # If the last val x is the same no movement


def mapping(val, in_min, in_max, out_min, out_max):
    val = max(in_min, min(in_max, val))
    # This functions as a clamp,which means it works from the inside out, so min(in_max,val) says i am chosing the smaller value of the two
    # so it can never be bigger than 65535, and max(in_min,min(...)) says i am chosing the bigger value of the two
    # which mean it can never be smaller than 800. So if a value is outside the parameters it gets pushed into the closest acepted value. 200=800 and 70_000=65_535
    return (val-in_min)*(out_max-out_min)/(in_max-in_min)+out_min
    # This function describs where we are in the input and converts to procent in the output
    # val-in_min makes it that our starting value is 0 insted of 800. Middel Value 32_317 and end value 64_635
    # Then divide to make it a % and add out_min to make up for that we start at 0 not 900


# Function to set angle (0 to 180 degrees)
def set_angle(angle):

    angle = max(0, min(180, angle))
    duty = int(mapping(angle, 0, 180, duty_min, duty_max))
    servo.duty_u16(duty)


# Test sweep
try:
    while True:
        x, y = read_axis()
        if last_x is None or abs(x-last_x) > Stick_drift:
            # if the last x value or the absolute value of x-last_x is greater than our stick drift run the code
            last_x = x
            angle = mapping(x, in_min, in_max, 0, 180)
            set_angle(angle)
           # print("moved:", int(angle), "Degres")
            time.sleep_ms(20)

except KeyboardInterrupt:
    servo.deinit()
