from machine import Pin, I2C
import ssd1306


class OledSkærm:
    def __init__(self, sda_pin=8, scl_pin=9, width=128, height=64, i2c_id=0):
        """
        Initialiserer I2C og OLED-skærmen.
        Standard-pins er GP8 (SDA) og GP9 (SCL) på Pico Bus 0.
        """
        self.width = width
        self.height = height

        # Opsæt I2C
        self.i2c = I2C(i2c_id, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=100000)

        # Initialiser SSD1306 skærmen
        self.oled = ssd1306.SSD1306_I2C(self.width, self.height, self.i2c)
        self.ryd()

    def ryd(self):
        """Rydder skærmen helt."""
        self.oled.fill(0)
        self.oled.show()

    def skriv_tekst(self, tekst, x, y, opdater=True):
        """Skriver tekst på specifikke x, y koordinater."""
        self.oled.text(tekst, x, y)
        if opdater:
            self.oled.show()

    def vis_servo_data(self, duty, vinkel):
        """
        En specialfunktion skræddersyet til dit servoprojekt.
        Opdaterer hele skærmen med de nyeste målinger.
        """
        self.oled.fill(0)  # Ryd skærmen i hukommelsen først (undgår flimmer)
        self.oled.text("SERVO STATUS", 15, 0)
        self.oled.text("----------------", 0, 12)
        self.oled.text(f"PWM Duty: {duty}", 0, 28)
        self.oled.text(f"Vinkel:  {vinkel:.1f}deg", 0, 44)
        self.oled.show()  # Send det hele til skærmen på én gang
