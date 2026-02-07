from smbus2 import SMBus
import time

PCF_ADDR = 0x27
I2C_BUS = 1

bus = SMBus(I2C_BUS)

def write_pcf16(value):
    """Write 16-bit value to PCF8575 (Port0 = bits 0-7, Port1 = bits 8-15)."""
    low_byte = value & 0xFF
    high_byte = (value >> 8) & 0xFF
    # Swap bytes if your board expects high byte first
    bus.write_i2c_block_data(PCF_ADDR, 0x00, [low_byte, high_byte])

try:
    # Set all relays off (assuming active-low)
    write_pcf16(0xFFFF)
    time.sleep(1)

    while True:
        # Turn on one relay at a time
        for i in range(16):
            value = 0xFFFF  # all off
            value &= ~(1 << i)  # set current relay ON (active-low)
            write_pcf16(value)
            print(f"Relay {i+1} ON")
            time.sleep(0.5)

        # Turn all relays off
        write_pcf16(0xFFFF)
        print("All relays OFF")
        time.sleep(1)

except KeyboardInterrupt:
    write_pcf16(0xFFFF)  # ensure all relays off on exit
    print("Exiting, all relays OFF")
