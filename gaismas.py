import time
from adafruit_mcp230xx import mcp23017
from adafruit_pcf8575 import PCF8575
from adafruit_mcp230xx.digital_inout import DigitalInOut
import board
import busio

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1)

# MCP23017 inputs
mcp1 = mcp23017.MCP23017(i2c, address=0x20)
mcp2 = mcp23017.MCP23017(i2c, address=0x21)

# PCF8575 relays
pcf1 = PCF8575(i2c, address=0x26)
pcf2 = PCF8575(i2c, address=0x27)

# Setup inputs
inputs = []
for pin in range(16):
    p = mcp1.get_pin(pin)
    p.switch_to_input()
    inputs.append(p)
for pin in range(16):
    p = mcp2.get_pin(pin)
    p.switch_to_input()
    inputs.append(p)

# Initialize relay states (all off, active-low)
relay_states = [False]*32
pcf1.write_gpio(0xFFFF)
pcf2.write_gpio(0xFFFF)

# Last button states
last_vals = [True]*32  # pull-ups assumed, so HIGH

while True:
    out1 = 0xFFFF
    out2 = 0xFFFF

    for i, inp in enumerate(inputs):
        val = inp.value
        # Toggle on falling edge (HIGH->LOW)
        if not val and last_vals[i]:
            relay_states[i] = not relay_states[i]

        last_vals[i] = val

        # Map relay state to PCF8575 (active-low)
        if relay_states[i]:
            if i < 16:
                out1 &= ~(1 << i)
            else:
                out2 &= ~(1 << (i - 16))

    # Write to relays
    pcf1.write_gpio(out1)
    pcf2.write_gpio(out2)

    time.sleep(0.05)
