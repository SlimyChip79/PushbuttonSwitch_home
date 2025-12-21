#!/usr/bin/env python3
import time
import board
import busio
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_mcp230xx.digital_inout import DigitalInOut
from adafruit_pcf8575 import PCF8575

# -------------------- I2C SETUP --------------------
i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1)  # bus stability

# -------------------- MCP23017 INPUTS --------------------
mcp1 = MCP23017(i2c, address=0x20)
mcp2 = MCP23017(i2c, address=0x21)

# NORMAL INPUTS (15)
normal_inputs_map = [(mcp1, i) for i in range(15)]
normal_inputs = []
for chip, pin in normal_inputs_map:
    p = DigitalInOut(chip.get_pin(pin))
    p.switch_to_input()
    normal_inputs.append(p)

# SPECIAL INPUTS (9 click/hold)
special_inputs_map = [(mcp1, 15)] + [(mcp2, i) for i in range(0, 8)]
special_inputs = []
for chip, pin in special_inputs_map:
    p = DigitalInOut(chip.get_pin(pin))
    p.switch_to_input()
    special_inputs.append(p)

# -------------------- PCF8575 RELAYS --------------------
pcf1 = PCF8575(i2c, address=0x26)
pcf2 = PCF8575(i2c, address=0x27)

# Set all relays OFF (active-low)
pcf1.write_gpio([1]*16)
pcf2.write_gpio([1]*16)
time.sleep(0.2)

# -------------------- CONFIG --------------------
DEBOUNCE_DELAY = 50          # ms
LONG_PRESS_THRESHOLD = 2000  # ms

normal_last_values = [0]*len(normal_inputs)
normal_states = [False]*len(normal_inputs)

special_last = [0]*len(special_inputs)
special_last_debounce = [0]*len(special_inputs)
special_press_start = [0]*len(special_inputs)
special_long_triggered = [False]*len(special_inputs)

# -------------------- RELAY MAPPING --------------------
normal_relays = list(range(15))         # 0-14
special_click_relays = list(range(15,24))  # 15-23
special_hold_relays  = list(range(24,33))  # 24-32

print("32-input (15 normal + 9 special) controller started")

# -------------------- LOOP --------------------
while True:
    current_time = int(time.time() * 1000)  # ms
    out1 = [1]*16
    out2 = [1]*16

    # NORMAL INPUTS
    for i, pin_obj in enumerate(normal_inputs):
        val = pin_obj.value
        if val and not normal_last_values[i]:
            normal_states[i] = not normal_states[i]
        normal_last_values[i] = val

        relay_pin = normal_relays[i]
        if normal_states[i]:
            if relay_pin < 16:
                out1[relay_pin] = 0
            else:
                out2[relay_pin - 16] = 0

    # SPECIAL CLICK/HOLD INPUTS
    for i, pin_obj in enumerate(special_inputs):
        reading = pin_obj.value
        if reading != special_last[i]:
            special_last_debounce[i] = current_time

        if (current_time - special_last_debounce[i]) > DEBOUNCE_DELAY:
            if reading:
                if special_press_start[i] == 0:
                    special_press_start[i] = current_time
                    special_long_triggered[i] = False
                elif not special_long_triggered[i] and (current_time - special_press_start[i] >= LONG_PRESS_THRESHOLD):
                    relay_pin = special_hold_relays[i]
                    if relay_pin < 16:
                        out1[relay_pin] = 0
                    else:
                        out2[relay_pin - 16] = 0
                    special_long_triggered[i] = True
            else:
                if special_press_start[i] != 0 and not special_long_triggered[i]:
                    relay_pin = special_click_relays[i]
                    if relay_pin < 16:
                        out1[relay_pin] = 0
                    else:
                        out2[relay_pin - 16] = 0
                special_press_start[i] = 0
                special_long_triggered[i] = False

        special_last[i] = reading

    # WRITE RELAYS
    pcf1.write_gpio(out1)
    pcf2.write_gpio(out2)

    # DEBUG OUTPUT
    print("\nNormal Inputs:", [p.value for p in normal_inputs])
    print("Special Inputs:", [p.value for p in special_inputs])
    print("PCF1:", out1)
    print("PCF2:", out2)

    time.sleep(0.05)
