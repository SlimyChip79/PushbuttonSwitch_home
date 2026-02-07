#!/usr/bin/env python3
import time
from smbus2 import SMBus

# ================= CONFIG =================
I2C_BUS = 1
PCA_ADDR = 0x20  # Input extender (PCA9555)
PCF_ADDR = 0x27  # Relay extender (PCF8575)

# ================= HELPERS =================
def log(msg):
    print(f"[GAISMAS] {time.strftime('%H:%M:%S')} | {msg}", flush=True)

def read_inputs(bus):
    """
    Read 16 inputs from PCA9555 (2 ports)
    Returns 16-bit integer: bit0 = input1, bit15 = input16
    """
    try:
        p0 = bus.read_byte_data(PCA_ADDR, 0x00)  # Input port 0
        p1 = bus.read_byte_data(PCA_ADDR, 0x01)  # Input port 1
        # Combine into 16-bit int
        inputs = (p1 << 8) | p0
        return inputs
    except OSError as e:
        log(f"PCA read error: {e}")
        return 0xFFFF  # Default all high if error

def write_relays_pcf(bus, relay_bits):
    """
    Write 16 relays to PCF8575 using working active-low method
    relay_bits: 16-bit int, bit0 = relay1, bit15 = relay16
    """
    # Map low/high bytes
    low_byte  = relay_bits & 0xFF       # relays 1-8
    high_byte = (relay_bits >> 8) & 0xFF  # relays 9-16

    # Invert for active-low relays
    low_byte  ^= 0xFF
    high_byte ^= 0xFF

    try:
        bus.write_byte_data(PCF_ADDR, 0x00, low_byte)
        time.sleep(0.01)
        bus.write_byte_data(PCF_ADDR, 0x01, high_byte)
        time.sleep(0.01)
    except OSError as e:
        log(f"PCF write error: {e}")

# ================= INIT =================
log("Service starting")

try:
    bus = SMBus(I2C_BUS)
    log("I2C bus opened")
except Exception as e:
    log(f"I2C init failed: {e}")
    bus = None

if bus:
    # Initialize PCA9555: all inputs
    try:
        bus.write_byte_data(PCA_ADDR, 0x06, 0xFF)  # Port 0 config input
        bus.write_byte_data(PCA_ADDR, 0x07, 0xFF)  # Port 1 config input
        log("PCA9555 configured (16 inputs)")
    except OSError as e:
        log(f"PCA init error: {e}")

    # Initialize PCF8575: all relays off
    write_relays_pcf(bus, 0x0000)
    log("PCF8575 relays cleared")

# ================= MAIN LOOP =================
prev_inputs = 0xFFFF  # Assume all high at start

try:
    while True:
        if not bus:
            time.sleep(1)
            continue

        inputs = read_inputs(bus)
        log(f"INPUTS : {inputs:016b}")

        # Map inputs directly to relays
        relay_bits = inputs  # 1=input high -> relay off, 0=input low -> relay on
        write_relays_pcf(bus, relay_bits)
        log(f"RELAYS : {relay_bits:016b}")

        time.sleep(1)

except KeyboardInterrupt:
    log("Service stopped by user")

finally:
    if bus:
        # Turn off all relays
        write_relays_pcf(bus, 0x0000)
        bus.close()
    log("Service exited")
