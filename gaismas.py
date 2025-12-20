import time
import board
import busio
from adafruit_pcf8575 import PCF8575

i2c = busio.I2C(board.SCL, board.SDA)
pcf = PCF8575(i2c, address=0x27)

RELAY_ON  = 0
RELAY_OFF = 1

def set_all(state):
    value = 0x0000 if state == RELAY_ON else 0xFFFF
    pcf.write_gpio(value)

def set_one(pin, state):
    value = 0xFFFF
    if state == RELAY_ON:
        value &= ~(1 << pin)
    pcf.write_gpio(value)

# 🔥 CRITICAL FIX: force OFF immediately
set_all(RELAY_OFF)

# Give hardware time to settle
time.sleep(0.5)

# Test: ON then OFF one by one
while True:
    for pin in range(16):
        set_one(pin, RELAY_ON)
        time.sleep(0.5)
        set_all(RELAY_OFF)
        time.sleep(0.2)
