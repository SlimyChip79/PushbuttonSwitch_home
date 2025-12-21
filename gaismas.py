import time
import board
import busio
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_mcp230xx.digital_inout import DigitalInOut
from adafruit_pcf8575 import PCF8575

# -------------------- I2C --------------------
i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1)

# -------------------- BOARDS --------------------
mcp_inputs = MCP23017(i2c, address=0x20)  # 16 inputs
pcf_relays = PCF8575(i2c, address=0x26)   # 16 relays

# -------------------- CONFIG --------------------
DEBOUNCE_DELAY = 50  # ms

# Map inputs to relays directly
inputs_map = [(mcp_inputs, i) for i in range(16)]
relays_map = list(range(16))

# -------------------- INIT --------------------
inputs = [DigitalInOut(chip, pin) for chip, pin in inputs_map]
for p in inputs: p.switch_to_input()

# Safety: all relays OFF (active-low)
pcf_relays.write_gpio(0xFFFF)
time.sleep(0.2)

# States
last_values = [0]*len(inputs)
toggle_states = [False]*len(inputs)

print("Simple toggle controller started")

# -------------------- LOOP --------------------
while True:
    out = 0xFFFF  # all relays OFF
    for i, pin_obj in enumerate(inputs):
        val = pin_obj.value
        if val and not last_values[i]:
            toggle_states[i] = not toggle_states[i]
        last_values[i] = val

        if toggle_states[i]:
            out &= ~(1 << relays_map[i])

    # Write relays
    pcf_relays.write_gpio(out)

    # Debug
    print("Inputs:", [p.value for p in inputs])
    print("Relays: {:016b}".format(out))

    time.sleep(0.05)
