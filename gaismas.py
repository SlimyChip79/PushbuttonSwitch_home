import time
import board
import busio
from adafruit_pcf8575 import PCF8575

# -------------------- I2C --------------------
i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1)

# -------------------- PCF8575 setup --------------------
pcf = PCF8575(i2c, address=0x27)

# Start with all relays OFF (active-low -> HIGH = off)
pcf.value = 0xFFFF

# -------------------- Blink relays one by one --------------------
while True:
    for i in range(8):  # pins 0–7
        mask = 1 << i

        # Turn relay ON (active-low)
        pcf.value &= ~mask
        time.sleep(0.5)

        # Turn relay OFF
        pcf.value |= mask
        time.sleep(0.5)
