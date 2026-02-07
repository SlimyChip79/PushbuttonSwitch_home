from smbus2 import SMBus
import time

PCF_ADDR = 0x27
I2C_BUS = 1

bus = SMBus(I2C_BUS)

def write_pcf16(value):
    """Write 16-bit value to PCF8575, swapped bytes for proper relay order"""
    low_byte = value & 0xFF
    high_byte = (value >> 8) & 0xFF
    bus.write_i2c_block_data(PCF_ADDR, 0x00, [high_byte, low_byte])

try:
    # Turn all relays off initially
    write_pcf16(0xFFFF)
    time.sleep(1)

    while True:
        for i in range(16):
            value = 0xFFFF  # all off
            value &= ~(1 << i)  # active-low, set current relay ON
            write_pcf16(value)
            print(f"Relay {i+1} ON")
            time.sleep(0.5)

        # Turn all relays off
        write_pcf16(0xFFFF)
        print("All relays OFF")
        time.sleep(1)

except KeyboardInterrupt:
    write_pcf16(0xFFFF)
    print("Exiting, all relays OFF")
