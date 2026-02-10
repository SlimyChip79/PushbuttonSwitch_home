import time
import board
import busio
from adafruit_pcf8575 import PCF8575

# -------------------- I2C SETUP --------------------
i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1)  # small delay for bus stability

# -------------------- PCF8575 RELAYS --------------------
pcf = PCF8575(i2c, address=0x27)

# set all relays OFF initially (active-low)
pcf.write_gpio(0xFFFF)

# -------------------- MAIN LOOP --------------------
while True:
    for i in range(16):
        mask = 1 << i
        # turn only this relay ON, rest OFF
        pcf.write_gpio(~mask & 0xFFFF)
        print(f"Relay {i} ON")
        time.sleep(0.5)
