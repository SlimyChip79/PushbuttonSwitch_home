#!/usr/bin/env python3
import time
import board
import busio
from adafruit_pcf8575 import PCF8575

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)

# PCF8575 address from i2cdetect
pcf = PCF8575(i2c, 0x27)

# Set all 16 pins as outputs
for pin in range(16):
    pcf.setup(pin, True)  # True = output

print("Starting 16-relay test (active-low)...")

try:
    while True:
        for pin in range(16):
            print(f"Relay {pin} ON")
            pcf.output(pin, False)  # Active LOW = ON
            time.sleep(0.5)
            print(f"Relay {pin} OFF")
            pcf.output(pin, True)   # OFF
        time.sleep(1)  # pause between cycles

except KeyboardInterrupt:
    # Turn all relays OFF on exit
    for pin in range(16):
        pcf.output(pin, True)
    print("Relay test stopped, all relays OFF")
