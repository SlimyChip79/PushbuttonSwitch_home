#!/usr/bin/env python3
import time
import board
import busio
from adafruit_pcf8575 import PCF8575
from digitalio import Direction

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)

# PCF8575 at address 0x27
pcf = PCF8575(i2c, 0x27)

# Create Pin objects for all 16 pins
# Create Pin objects for all pins
pins = [pcf.get_pin(i) for i in range(16)]

# Immediately set all pins HIGH (OFF)
for pin in pins:
    pin.value = True

# Then set direction to OUTPUT
for pin in pins:
    pin.direction = Direction.OUTPUT


print("Starting sequence...")

while True:
    # Turn pins ON one by one
    for pin in pins:
        pin.value = False  # LOW = ON
        time.sleep(0.5)

    # Turn pins OFF one by one
    for pin in pins:
        pin.value = True   # HIGH = OFF
        time.sleep(0.5)
