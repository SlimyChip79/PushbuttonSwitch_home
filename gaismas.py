import time
from smbus2 import SMBus

# ================= CONFIG =================

I2C_BUS = 1

PCA_ADDR = 0x21   # input expander
PCF_ADDR = 0x20   # relay expander

POLL_INTERVAL = 1.0  # seconds

# =========================================

bus = SMBus(I2C_BUS)

# --- PCA9555 setup: all pins INPUT ---
bus.write_byte_data(PCA_ADDR, 0x06, 0xFF)  # port 0 config
bus.write_byte_data(PCA_ADDR, 0x07, 0xFF)  # port 1 config

# PCF8575 relay state (1 = OFF, 0 = ON)
pcf_state = 0xFFFF


def read_pca_inputs():
    low = bus.read_byte_data(PCA_ADDR, 0x00)   # inputs 1–8
    high = bus.read_byte_data(PCA_ADDR, 0x01)  # inputs 9–16
    return (high << 8) | low


def write_pcf(value):
    bus.write_word_data(PCF_ADDR, 0x00, value)


# Initialize relays OFF
write_pcf(pcf_state)

print("[GAISMAS] Service started")
print("[GAISMAS] PCA9555 → PCF8575 polling")

try:
    while True:
        inputs = read_pca_inputs()

        # Direct 1:1 mapping
        # PCA bit = relay bit
        # PCA LOW  -> relay ON
        # PCA HIGH -> relay OFF
        pcf_state = inputs  # invert if needed below
        pcf_state ^= 0xFFFF  # because relays are active LOW

        write_pcf(pcf_state)

        print(f"[GAISMAS] PCA={inputs:016b}  PCF={pcf_state:016b}")
        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    pass
finally:
    write_pcf(0xFFFF)
    bus.close()
    print("[GAISMAS] Stopped")
