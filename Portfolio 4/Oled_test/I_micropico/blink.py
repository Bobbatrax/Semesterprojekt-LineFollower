from machine import Pin, PWM, ADC
from time import sleep
import _thread

# 1. IMPORTER DIN NYE CLASS FRA DEN ANDEN FIL
from Servo import OledSkærm

# Initialiser skærmen (Bruger standard GP8/SDA og GP9/SCL)
skærm = OledSkærm()

# --- HARDWARE SETUP ---
servo_pin = Pin(0, Pin.OUT)
servo = PWM(servo_pin)
servo.freq(50)

min_duty = 1802
max_duty = 7864
half_duty = int((max_duty + min_duty) / 2)

potmeter = ADC(Pin(26))
ADC_MIN = 500
ADC_MAX = 65000

# --- BAGGRUNDS-TRÅD TIL LOGNING OG SKÆRM ---


def maale_traad():
    while True:
        udsendt_duty = servo.duty_u16()
        fysisk_adc = potmeter.read_u16()

        if (ADC_MAX - ADC_MIN) != 0:
            fysisk_vinkel = ((fysisk_adc - ADC_MIN) /
                             (ADC_MAX - ADC_MIN)) * 180
            fysisk_vinkel = max(0, min(180, fysisk_vinkel))
        else:
            fysisk_vinkel = 0

        # 2. BRUG KLASSENS FUNKTION TIL AT OPDATERE SKÆRMEN
        skærm.vis_servo_data(udsendt_duty, fysisk_vinkel)

        # Print i konsol samtidig
        print(
            f"[PWM ud]: {udsendt_duty:<5} | [Ægte vinkel]: {fysisk_vinkel:>5.1f}°")

        # Opdater skærmen 5 gange i sekundet (forhindrer unødigt tråd-stress)
        sleep(0.2)


# Start måling og skærmopdatering
_thread.start_new_thread(maale_traad, ())

# --- HOVEDPROGRAM ---
try:
    skærm.skriv_tekst("Starter...", 0, 0)
    sleep(1)

    while True:
        servo.duty_u16(min_duty)
        sleep(2)
        servo.duty_u16(half_duty)
        sleep(2)
        servo.duty_u16(max_duty)
        sleep(2)

except KeyboardInterrupt:
    print("\nProgrammet stoppet.")
    skærm.ryd()
    skærm.skriv_tekst("System lukket", 10, 25)
    servo.deinit()
