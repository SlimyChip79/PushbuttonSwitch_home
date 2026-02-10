from adafruit_pcf8574 import PCF8574
import busio
import board
import time

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)
pcf = PCF8574(i2c, address=0x27)

# Create pins 0-7
pins = [pcf.get_pin(i) for i in range(8)]

# Set all pins as outputs
for p in pins:
    p.direction = True  # True = OUTPUT

# Blink relays one by one
while True:
    for p in pins:
        p.value = True   # ON
        time.sleep(0.5)
        p.value = False  # OFF
