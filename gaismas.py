import time
import board
import busio
from adafruit_mcp230xx import mcp23017
from adafruit_pcf8575 import PCF8575
from adafruit_mcp230xx.digital_inout import DigitalInOut

# -------------------- I2C SETUP --------------------
i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1)  # small delay for bus stability

# -------------------- INPUT BOARDS --------------------
try:
    mcp1 = mcp23017.MCP23017(i2c, address=0x20)
    time.sleep(0.1)  # stabilize bus
    mcp2 = mcp23017.MCP23017(i2c, address=0x21)
except OSError as e:
    print("Error initializing MCP23017 boards:", e)
    raise SystemExit

# -------------------- RELAY BOARDS --------------------
pcf1 = PCF8575(i2c, address=0x26)
pcf2 = PCF8575(i2c, address=0x27)

# -------------------- INPUTS --------------------
inputs = []
for pin in range(16):
    p = DigitalInOut(mcp1.get_pin(pin))
    p.switch_to_input()
    inputs.append(p)
for pin in range(16):
    p = DigitalInOut(mcp2.get_pin(pin))
    p.switch_to_input()
    inputs.append(p)

# -------------------- RELAYS --------------------
relay_states = [False]*32  # all OFF at start
out1 = 0xFFFF  # PCF8575 HIGH = OFF
out2 = 0xFFFF
pcf1.write_gpio(out1)
pcf2.write_gpio(out2)
time.sleep(0.1)

# -------------------- BUTTON TRACKING --------------------
last_values = [0]*32

print("32-button pushbutton controller started (HIGH = active, LOW = relay ON)")

# -------------------- MAIN LOOP --------------------
while True:
    for i, inp in enumerate(inputs):
        current = inp.value  # HIGH when pressed
        # Rising edge detection (button pressed)
        if current and not last_values[i]:
            relay_states[i] = not relay_states[i]  # toggle relay

        last_values[i] = current

        # Update outputs
        if i < 16:
            if relay_states[i]:
                out1 &= ~(1 << i)  # LOW = ON
            else:
                out1 |= (1 << i)   # HIGH = OFF
        else:
            idx = i - 16
            if relay_states[i]:
                out2 &= ~(1 << idx)
            else:
                out2 |= (1 << idx)

    # Write to relay boards
    pcf1.write_gpio(out1)
    pcf2.write_gpio(out2)

    # Optional debug
    # print([inp.value for inp in inputs])
    # print([int(r) for r in relay_states])

    time.sleep(0.05)
