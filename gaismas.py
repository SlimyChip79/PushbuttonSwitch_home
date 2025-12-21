import time
import board
import busio
from adafruit_mcp230xx import mcp23017
from adafruit_pcf8575 import PCF8575

# ================= I2C =================
i2c = busio.I2C(board.SCL, board.SDA)

# ============ INPUT EXPANDERS ==========
mcp1 = mcp23017.MCP23017(i2c, address=0x20)
mcp2 = mcp23017.MCP23017(i2c, address=0x21)

# ============ RELAY EXPANDERS ==========
pcf1 = PCF8575(i2c, address=0x26)
pcf2 = PCF8575(i2c, address=0x27)

# ======== RELAY LOGIC (ACTIVE LOW) =====
RELAY_ON  = 0
RELAY_OFF = 1

# ============ INPUT SETUP ==============
inputs1 = [mcp1.get_pin(pin) for pin in range(16)]
inputs2 = [mcp2.get_pin(pin) for pin in range(16)]

for p in inputs1 + inputs2:
    p.switch_to_input()  # external pull-down resistors

# ============ STATE MEMORY =============
lastState1  = [False] * 16
lastState2  = [False] * 16

relayState1 = [False] * 16  # False=OFF, True=ON
relayState2 = [False] * 16

# ============ SAFETY OFF ===============
pcf1.write_gpio(0xFFFF)
pcf2.write_gpio(0xFFFF)
time.sleep(0.2)

print("=== 32 PUSHBUTTON → 32 RELAY TOGGLE SYSTEM STARTED ===")

# ================= LOOP =================
while True:

    # -------- MCP 0x20 --------
    for pin in range(16):
        currentState = inputs1[pin].value  # LOW=False, HIGH=True

        # BUTTON PRESS (LOW → HIGH)
        if currentState and not lastState1[pin]:
            relayState1[pin] = not relayState1[pin]
            print(f"[MCP 0x20] Button {pin} → Relay {'ON' if relayState1[pin] else 'OFF'}")

        lastState1[pin] = currentState

    # -------- MCP 0x21 --------
    for pin in range(16):
        currentState = inputs2[pin].value

        if currentState and not lastState2[pin]:
            relayState2[pin] = not relayState2[pin]
            print(f"[MCP 0x21] Button {pin} → Relay {'ON' if relayState2[pin] else 'OFF'}")

        lastState2[pin] = currentState

    # -------- WRITE RELAYS --------
    out1 = 0xFFFF
    out2 = 0xFFFF

    for pin in range(16):
        if relayState1[pin]:
            out1 &= ~(1 << pin)   # ACTIVE LOW → ON
        if relayState2[pin]:
            out2 &= ~(1 << pin)

    pcf1.write_gpio(out1)
    pcf2.write_gpio(out2)

    time.sleep(0.05)  # debounce / CPU friendly
