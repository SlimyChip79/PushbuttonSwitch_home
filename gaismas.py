#!/usr/bin/env python3
import time
from pcf8575 import PCF8575
from smbus2 import SMBus
import RPi.GPIO as GPIO

# ================== CONFIG ==================
# PCF8575 relay board
PCF_ADDR = 0x27
I2C_BUS = 1

# PCA9555 input extender
PCA_ADDR = 0x20
REG_INPUT_0  = 0x00
REG_INPUT_1  = 0x01
REG_OUTPUT_1 = 0x03
REG_CONFIG_0 = 0x06
REG_CONFIG_1 = 0x07
INT_PIN = 17   # PCA9555 interrupt pin

POLL_INTERVAL = 0.02  # 20ms

# ================== GPIO SETUP ==================
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(INT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ================== I2C SETUP ==================
bus = SMBus(I2C_BUS)

# ---------------- PCF8575 -------------------
print("[RELAYS] Initializing PCF8575...")
pcf = PCF8575(I2C_BUS, PCF_ADDR)

# Turn all relays OFF first (active-low)
for i in range(16):
    pcf[i] = 1

time.sleep(0.5)
print("[RELAYS] Ready")

# ---------------- PCA9555 -------------------
def setup_pca():
    # P0 inputs, P1 outputs (not used, just safe)
    bus.write_byte_data(PCA_ADDR, REG_CONFIG_0, 0xFF)
    bus.write_byte_data(PCA_ADDR, REG_CONFIG_1, 0x00)
    bus.write_byte_data(PCA_ADDR, REG_OUTPUT_1, 0x00)
    print("[PCA] Configured")

setup_pca()

def read_pca_inputs():
    p0 = bus.read_byte_data(PCA_ADDR, REG_INPUT_0)
    p1 = bus.read_byte_data(PCA_ADDR, REG_INPUT_1)
    # Combine into 16 bits
    return [(p0 >> i) & 1 for i in range(8)] + [(p1 >> i) & 1 for i in range(8)]

# ================== MAIN LOOP ==================
relay_states = [False] * 16  # initial state
last_input_values = [0] * 16

print("[MAIN] Starting loop")
try:
    while True:
        # Read PCA9555 inputs
        inputs = read_pca_inputs()

        # Check rising edges and toggle relays like the example
        for i, val in enumerate(inputs):
            if val == 0 and last_input_values[i] == 1:  # active-low pressed
                relay_states[i] = not relay_states[i]  # toggle

            last_input_values[i] = val

            # Apply to PCF relays
            pcf[i] = 0 if relay_states[i] else 1

        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    print("\n[MAIN] Stopping, turning all relays OFF")
    for i in range(16):
        pcf[i] = 1
finally:
    GPIO.cleanup()
    bus.close()
    print("[MAIN] Clean exit")
