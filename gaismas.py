#!/usr/bin/env python3
from smbus2 import SMBus
import time

I2C_BUS = 1
PCF_ADDR = 0x27  # your PCF8575 address
DELAY = 1  # seconds

def write_relays(bus, relay_bits):
    """Writes 16-bit value to PCF8575 with active-low relays."""
    # PCF8575 expects: low_byte = P0-P7, high_byte = P8-P15
    # Our board mapping: first 8 relays are physical P8-P15, next 8 relays P0-P7
    high_byte = relay_bits & 0xFF       # relays 1-8 physically
    low_byte  = (relay_bits >> 8) & 0xFF  # relays 9-16 physically
    # invert bits for active-low
    high_byte ^= 0xFF
    low_byte  ^= 0xFF
    try:
        bus.write_byte_data(PCF_ADDR, 0x00, low_byte)
        time.sleep(0.01)  # small delay to let board latch
        bus.write_byte_data(PCF_ADDR, 0x01, high_byte)
        time.sleep(0.01)
    except Exception as e:
        print(f"PCF write error: {e}")

def main():
    bus = SMBus(I2C_BUS)
    try:
        print("Clearing all relays...")
        write_relays(bus, 0x0000)  # all off
        time.sleep(1)

        for i in range(16):
            relay_state = 1 << i  # turn one relay on
            print(f"Relay {i+1} ON")
            write_relays(bus, relay_state)
            time.sleep(DELAY)

            print(f"Relay {i+1} OFF")
            write_relays(bus, 0x0000)
            time.sleep(DELAY)

    finally:
        print("Clearing all relays at end")
        write_relays(bus, 0x0000)
        bus.close()

if __name__ == "__main__":
    main()
