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
inputs1 = [mcp1.get_pin(pin) for pin in range(16)]
inputs2 = [mcp2.get_pin(pin) for pin in range(16)]

for p in inputs1 + inputs2:
    p.switch_to_input()  # pulled-down inputs

# -------- Safety: all relays OFF -------
pcf1.write_gpio(0xFFFF)
pcf2.write_gpio(0xFFFF)
time.sleep(0.2)

print("32 input → 32 relay controller started (debug mode)")

# ---------------- LOOP ----------------
while True:
    out1 = 0xFFFF
    out2 = 0xFFFF

    # ----- read MCP #1 -----
    input_vals1 = []
    for pin in range(16):
        val = inputs1[pin].value
        input_vals1.append(val)
        if val:
            out1 &= ~(1 << pin)  # active-low relay ON

    # ----- read MCP #2 -----
    input_vals2 = []
    for pin in range(16):
        val = inputs2[pin].value
        input_vals2.append(val)
        if val:
            out2 &= ~(1 << pin)

    # ----- print debug info -----
    print("\nInputs MCP 0x20:", ["HIGH" if v else "LOW" for v in input_vals1])
    print("Relay out PCF 0x26: {:016b}".format(out1))
    print("Inputs MCP 0x21:", ["HIGH" if v else "LOW" for v in input_vals2])
    print("Relay out PCF 0x27: {:016b}".format(out2))

    # ----- write to relays -----
    pcf1.write_gpio(out1)
    pcf2.write_gpio(out2)

    time.sleep(0.1)  # 10 Hz update
