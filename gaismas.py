import time
import board
import busio
from adafruit_mcp230xx import mcp23017
from adafruit_pcf8575 import PCF8575

# I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# MCP23017 input boards
mcp1 = mcp23017.MCP23017(i2c, address=0x20)
mcp2 = mcp23017.MCP23017(i2c, address=0x21)

# PCF8575 relay boards
pcf1 = PCF8575(i2c, address=0x26)
pcf2 = PCF8575(i2c, address=0x27)

# ACTIVE-LOW relay logic
RELAY_ON  = 0
RELAY_OFF = 1

# Inputs
inputs1 = [mcp1.get_pin(pin) for pin in range(16)]
inputs2 = [mcp2.get_pin(pin) for pin in range(16)]

for p in inputs1 + inputs2:
    p.switch_to_input()  # external pull-down

# --- Arduino-style state variables ---
lastState1 = [True] * 16   # assume HIGH → matches Arduino pull-up logic
lastState2 = [True] * 16

relayState1 = [False] * 16
relayState2 = [False] * 16

# Safety: all relays OFF
pcf1.write_gpio(0xFFFF)
pcf2.write_gpio(0xFFFF)
time.sleep(0.2)

print("Arduino-style pushbutton toggle logic started")

while True:
    # ----- MCP #1 -----
    for pin in range(16):
        currentState = inputs1[pin].value

        # SAME LOGIC AS YOUR ARDUINO CODE
        if currentState == False and lastState1[pin] == True:
            relayState1[pin] = not relayState1[pin]
            print(f"MCP 0x20 pin {pin} toggled → {'ON' if relayState1[pin] else 'OFF'}")

        lastState1[pin] = currentState

    # ----- MCP #2 -----
    for pin in range(16):
        currentState = inputs2[pin].value

        if currentState == False and lastState2[pin] == True:
            relayState2[pin] = not relayState2[pin]
            print(f"MCP 0x21 pin {pin} toggled → {'ON' if relayState2[pin] else 'OFF'}")

        lastState2[pin] = currentState

    # ----- Write relays -----
    out1 = 0xFFFF
    out2 = 0xFFFF

    for pin in range(16):
        if relayState1[pin]:
            out1 &= ~(1 << pin)
        if relayState2[pin]:
            out2 &= ~(1 << pin)

    pcf1.write_gpio(out1)
    pcf2.write_gpio(out2)

    time.sleep(0.05)
