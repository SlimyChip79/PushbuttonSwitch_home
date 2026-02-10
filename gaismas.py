from adafruit_pcf8574 import PCF8574
import busio
import board
import time

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
pcf = PCF8574(i2c, address=0x27)

# Setup pins
pins = [pcf.get_pin(i) for i in range(8)]

# Set all pins as OUTPUT using the proper constant
for p in pins:
    p.direction = PCF8574.OUTPUT  # <-- this is the correct way

# Blink relays one by one
while True:
    for p in pins:
        p.value = True   # ON
        time.sleep(0.5)
        p.value = False  # OFF
