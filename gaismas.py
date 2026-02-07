#!/usr/bin/env python3
from smbus2 import SMBus
import time

# ================= CONFIG =================
I2C_BUS = 1
PCF_ADDR = 0x27
DELAY = 1  # seconds to hold relay on

# ================= START =================
print("[GAISMAS] Relay test starting")

try:
    bus = SMBus(I2C_BUS)
    print("[GAISMAS] I2C bus opened")
except Exception as e:
    print(f"[GAISMAS] I2C init failed: {e}")
    bus = None

# ================= HELPER =================
def write_pcf(relay_state):
    """
    Write 16-bit relay_state to PCF8575.
    relay_state: 16-bit int, bit0 = relay 1 (board's physical first relay)
    """
    if not bus:
        return

    # flip bytes because board's first 8 relays are P8-P15
    # P8-P15 -> low_byte, P0-P7 -> high_byte
    high_byte = relay_state & 0xFF       # bits 0-7 = relays 9-16 physically
    low_byte  = (relay_state >> 8) & 0xFF  # bits 8-15 = relays 1-8 physically

    try:
        bus.write_byte_data(PCF_ADDR, 0x00, low_byte)   # physical relays 1-8
        time.sleep(0.002)
        bus.write_byte_data(PCF_ADDR, 0x01, high_byte)  # physical relays 9-16
    except Exception as e:
        print(f"[GAISMAS] PCF write error: {e}")

# ================= MAIN LOOP =================
try:
    # all relays off at start
    relay_state = 0xFFFF
    write_pcf(relay_state)
    print("[GAISMAS] All relays cleared")
    time.sleep(1)

    while True:
        for i in range(16):
            # turn on this relay (active low)
            relay_state = 0xFFFF ^ (1 << i)
            write_pcf(relay_state)
            print(f"[GAISMAS] Relay {i+1} ON")
            time.sleep(DELAY)

            # turn off
            relay_state = 0xFFFF
            write_pcf(relay_state)
            print(f"[GAISMAS] Relay {i+1} OFF")
            time.sleep(DELAY)

except KeyboardInterrupt:
    print("[GAISMAS] Test stopped by user")

finally:
    relay_state = 0xFFFF
    write_pcf(relay_state)
    print("[GAISMAS] All relays cleared")
    if bus:
        bus.close()
