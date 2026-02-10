#!/usr/bin/env python3
import time
from pcf8575 import PCF8575
from smbus2 import SMBus

# -------------------- CONFIG --------------------
PCF_ADDR = 0x27
PCA_ADDR = 0x20
I2C_BUS = 1

# PCA registers
REG_OUTPUT_1 = 0x03
REG_CONFIG_0 = 0x06
REG_CONFIG_1 = 0x07

# -------------------- INIT --------------------
# PCF8575
pcf = PCF8575(I2C_BUS, PCF_ADDR)
for i in range(16):
    pcf.pin(i, 1)  # all OFF

# PCA9555
bus = SMBus(I2C_BUS)
bus.write_byte_data(PCA_ADDR, REG_CONFIG_0, 0xFF)  # P0 inputs (unused)
bus.write_byte_data(PCA_ADDR, REG_CONFIG_1, 0x00)  # P1 outputs
bus.write_byte_data(PCA_ADDR, REG_OUTPUT_1, 0xFF)  # all OFF (active low)

# -------------------- RELAY CONTROL FUNCTION --------------------
def set_relay(index, state):
    """
    index: 0..31
    state: True=ON, False=OFF (active-low assumed)
    """
    if index < 16:
        # PCF8575
        pcf.pin(index, 0 if state else 1)
    else:
        # PCA9555
        relay_idx = index - 16
        val = bus.read_byte_data(PCA_ADDR, REG_OUTPUT_1)
        if state:
            val &= ~(1 << relay_idx)  # ON = 0
        else:
            val |= (1 << relay_idx)   # OFF = 1
        bus.write_byte_data(PCA_ADDR, REG_OUTPUT_1, val)

# -------------------- EXAMPLE USAGE --------------------
try:
    # Example: turn some relays ON
    set_relay(0, True)    # PCF first relay ON
    set_relay(15, True)   # PCF last relay ON
    set_relay(16, True)   # PCA first relay ON
    set_relay(31, True)   # PCA last relay ON

    # Keep running, you can later poll inputs or set relays dynamically
    while True:
        time.sleep(0.5)

except KeyboardInterrupt:
    # turn everything off before exit
    for i in range(32):
        set_relay(i, False)
