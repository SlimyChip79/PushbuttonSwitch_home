from smbus2 import SMBus
import time
from datetime import datetime

# ================= CONFIG =================
I2C_BUS = 1

PCA_ADDR = 0x20      # INPUT expander (PCA9555)
PCF_ADDR = 0x27      # RELAY expander (PCF8575)

# PCA9555 registers
REG_INPUT_0  = 0x00
REG_INPUT_1  = 0x01
REG_CONFIG_0 = 0x06
REG_CONFIG_1 = 0x07

# ================= LOG =================
def log(msg):
    print(f"[GAISMAS] {datetime.now().strftime('%H:%M:%S')} | {msg}", flush=True)

# ================= START =================
log("Service starting")

bus = SMBus(I2C_BUS)
log("I2C bus opened")

# ================= PCA SETUP =================
# All 16 pins as INPUTS
bus.write_byte_data(PCA_ADDR, REG_CONFIG_0, 0xFF)
bus.write_byte_data(PCA_ADDR, REG_CONFIG_1, 0xFF)
log("PCA9555 configured (16 inputs)")

# ================= PCF SETUP =================
# All relays OFF (HIGH)
bus.write_word_data(PCF_ADDR, 0x00, 0xFFFF)
log("PCF8575 relays cleared")

last_inputs = None

# ================= MAIN LOOP =================
while True:
    try:
        # Read PCA inputs
        p0 = bus.read_byte_data(PCA_ADDR, REG_INPUT_0)
        p1 = bus.read_byte_data(PCA_ADDR, REG_INPUT_1)
        inputs = (p1 << 8) | p0

        # Only act on change
        if inputs != last_inputs:
            # Active LOW inputs → Active LOW relays
            relays = inputs  # direct 1:1 mapping
            bus.write_word_data(PCF_ADDR, 0x00, relays)

            log(f"INPUTS : {inputs:016b}")
            log(f"RELAYS : {relays:016b}")

            last_inputs = inputs

        time.sleep(0.05)  # 50ms polling

    except Exception as e:
        log(f"I2C error: {e}")
        time.sleep(1)
