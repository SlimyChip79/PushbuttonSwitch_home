import time
import board
import busio
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_pcf8575 import PCF8575

# ---------------- I2C ----------------
i2c = busio.I2C(board.SCL, board.SDA)

# ----------- Input expanders ----------
mcp1 = MCP23017(i2c, address=0x20)
mcp2 = MCP23017(i2c, address=0x21)

# ----------- Relay expanders ----------
pcf1 = PCF8575(i2c, address=0x26)
pcf2 = PCF8575(i2c, address=0x27)

# -------- Relay logic (ACTIVE LOW) ----
RELAY_ON  = 0
RELAY_OFF = 1

# -------- Initialize inputs -----------
inputs1 = []
inputs2 = []

for pin in range(16):
    p1 = mcp1.get_pin(pin)
    p2 = mcp2.get_pin(pin)

    p1.switch_to_input()  # external pull-down
    p2.switch_to_input()

    inputs1.append(p1)
    inputs2.append(p2)

# -------- Safety: all relays OFF -------
pcf1.write_gpio(0xFFFF)
pcf2.write_gpio(0xFFFF)
time.sleep(0.2)

print("32 input → 32 relay controller started")

# ---------------- LOOP ----------------
while True:
    out1 = 0xFFFF
    out2 = 0xFFFF

    # MCP 0x20 → PCF 0x26
    for pin in range(16):
        if inputs1[pin].value:        # HIGH input
            out1 &= ~(1 << pin)       # relay ON

    # MCP 0x21 → PCF 0x27
    for pin in range(16):
        if inputs2[pin].value:
            out2 &= ~(1 << pin)

    pcf1.write_gpio(out1)
    pcf2.write_gpio(out2)

    time.sleep(0.01)  # 100 Hz update, fast & stable
