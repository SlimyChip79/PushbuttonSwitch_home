import time
import board
import busio
from adafruit_mcp230xx import mcp23017
from adafruit_pcf8575 import PCF8575
from adafruit_mcp230xx.digital_inout import DigitalInOut

# -------------------- I2C SETUP --------------------
i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1)  # small delay for bus stability

# MCP23017 input boards
mcp1 = mcp23017.MCP23017(i2c, address=0x20)
mcp2 = mcp23017.MCP23017(i2c, address=0x21)

# PCF8575 relay boards
pcf1 = PCF8575(i2c, address=0x26)
pcf2 = PCF8575(i2c, address=0x27)

# -------------------- INPUT SETUP --------------------
# 32 pushbuttons mapped to 2 MCP23017 boards
inputs_pins = list(range(16)) + list(range(16))  # 0–15 on each board
inputs_board = [mcp1]*16 + [mcp2]*16

inputs = [DigitalInOut(board, pin) for board, pin in zip(inputs_board, inputs_pins)]
for p in inputs:
    p.switch_to_input()  # default pull-down (reads LOW when pressed)

# -------------------- RELAY STATE --------------------
relay_states = [False]*32  # all OFF initially
# active-low -> HIGH = off
pcf1.write_gpio(0xFFFF)
pcf2.write_gpio(0xFFFF)

# -------------------- BUTTON STATE TRACKING --------------------
last_input_values = [False]*32

print("32-input pushbutton controller started")

# -------------------- MAIN LOOP --------------------
while True:
    for i, pin_obj in enumerate(inputs):
        current_value = pin_obj.value
        if current_value and not last_input_values[i]:  # rising edge
            relay_states[i] = not relay_states[i]      # toggle relay

        last_input_values[i] = current_value

        # write relays to PCF8575
        relay_pin = i
        if relay_pin < 16:
            mask = 1 << relay_pin
            if relay_states[i]:
                pcf1.value &= ~mask  # ON
            else:
                pcf1.value |= mask   # OFF
        else:
            mask = 1 << (relay_pin - 16)
            if relay_states[i]:
                pcf2.value &= ~mask  # ON
            else:
                pcf2.value |= mask   # OFF

    # apply relay states
    pcf1.write_gpio(pcf1.value)
    pcf2.write_gpio(pcf2.value)

    # optional debug
    print([p.value for p in inputs])
    print([int(r) for r in relay_states])

    time.sleep(0.05)
