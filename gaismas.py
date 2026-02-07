#!/usr/bin/env python3
import time
from smbus2 import SMBus

# I2C settings
I2C_BUS = 1
PCF_ADDR = 0x27  # PCF8575 relay board

# Initialize relay states (all off)
relays = [0] * 16  # 0=off, 1=on
bus = SMBus(I2C_BUS)

def write_pcf(relays):
    """
    Write 16 relays to PCF8575
    Each element in relays list corresponds to 1 relay (0=off, 1=on)
    PCF8575 is active-low, so we invert bits
    """
    value = 0
    for i, state in enumerate(relays):
        if state:
            value |= (1 << i)
    # Active-low: invert
    value ^= 0xFFFF
    low_byte  = value & 0xFF
    high_byte = (value >> 8) & 0xFF

    bus.write_byte_data(PCF_ADDR, 0x00, low_byte)
    time.sleep(0.01)
    bus.write_byte_data(PCF_ADDR, 0x01, high_byte)
    time.sleep(0.01)

def test_relays():
    """
    Cycle through all 16 relays, turning them on one by one
    """
    try:
        while True:
            for i in range(16):
                # Turn all off first
                for j in range(16):
                    relays[j] = 0
                # Turn current relay on
                relays[i] = 1
                write_pcf(relays)
                print(f"RELAYS: {''.join(str(r) for r in relays)}")
                time.sleep(1)
            # Turn all off
            for j in range(16):
                relays[j] = 0
            write_pcf(relays)
            print("RELAYS: all off")
            time.sleep(1)
    except KeyboardInterrupt:
        for j in range(16):
            relays[j] = 0
        write_pcf(relays)
        print("Test stopped, all relays off")
    finally:
        bus.close()

if __name__ == "__main__":
    print("Starting PCF8575 relay test...")
    test_relays()
