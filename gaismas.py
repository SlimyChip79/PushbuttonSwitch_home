#!/usr/bin/env python3
import time
from smbus2 import SMBus
import board
import busio
from adafruit_pcf8575 import PCF8575

# ---------------- CONFIG ----------------
I2C_BUS = 1
PCA_ADDR = 0x20       # PCA9555 input extender
PCF_ADDR = 0x27       # PCF8575 relay board

REG_INPUT_0  = 0x00
REG_INPUT_1  = 0x01

POLL_INTERVAL = 0.02  # 20 ms

# ---------------- INIT ----------------
print("[GAISMAS] Initializing I2C and boards...")

# PCA9555 for inputs
bus = SMBus(I2C_BUS)

# PCF8575 for relays
i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1)
pcf = PCF8575(i2c, address=PCF_ADDR)
pcf.write_gpio(0xFFFF)  # all relays OFF

# track input and relay states
last_input = [1]*16       # PCA9555 inputs are active-low, default HIGH
pcf_state = 0xFFFF

print("[GAISMAS] Ready")

# ---------------- MAIN LOOP ----------------
try:
    while True:
        # read PCA9555 inputs
        p0 = bus.read_byte_data(PCA_ADDR, REG_INPUT_0)
        p1 = bus.read_byte_data(PCA_ADDR, REG_INPUT_1)
        inputs = [(p0 >> i) & 1 for i in range(8)] + [(p1 >> i) & 1 for i in range(8)]

        for i, val in enumerate(inputs):
            if val == 0 and last_input[i] == 1:  # button pressed
                # toggle relay i
                mask = 1 << i
                if pcf_state & mask:  # currently OFF
                    pcf_state &= ~mask  # turn ON
                    print(f"Relay {i+1} ON")
                else:
                    pcf_state |= mask   # turn OFF
                    print(f"Relay {i+1} OFF")

                # write updated state to PCF8575
                pcf.write_gpio(pcf_state)

            last_input[i] = val

        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    print("[GAISMAS] Stopping, turning all relays OFF")
    pcf.write_gpio(0xFFFF)
    bus.close()
