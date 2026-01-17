from smbus2 import SMBus
import RPi.GPIO as GPIO
import time
import sys

def log(msg):
    print(f"[GAISMAS] {msg}", flush=True)

# ================= CONFIG =================
I2C_BUS = 1
PCA_ADDR = 0x20
INT_PIN = 17

REG_INPUT_0 = 0x00
REG_INPUT_1 = 0x01
REG_OUTPUT_1 = 0x03
REG_CONFIG_0 = 0x06
REG_CONFIG_1 = 0x07

# ================= START =================
log("Service starting")

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(INT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# I2C setup
try:
    bus = SMBus(I2C_BUS)
    log("I2C bus opened")
except Exception as e:
    log(f"I2C init failed: {e}")
    bus = None

# PCA setup
def pca_setup():
    if not bus:
        return False
    try:
        bus.write_byte_data(PCA_ADDR, REG_CONFIG_0, 0xFF)  # inputs
        bus.write_byte_data(PCA_ADDR, REG_CONFIG_1, 0x00)  # outputs
        bus.write_byte_data(PCA_ADDR, REG_OUTPUT_1, 0x00)
        log("PCA9555 configured")
        return True
    except Exception as e:
        log(f"PCA config failed (board not connected?): {e}")
        return False

pca_ready = pca_setup()

# ================= FUNCTIONS =================
def read_inputs():
    return (
        bus.read_byte_data(PCA_ADDR, REG_INPUT_0),
        bus.read_byte_data(PCA_ADDR, REG_INPUT_1)
    )

def interrupt_cb(channel):
    if not pca_ready:
        log("INT ignored (PCA not ready)")
        return
    try:
        p0, p1 = read_inputs()  # clears interrupt
        log(f"INT | P0={p0:08b} P1={p1:08b}")

        # Example: mirror inputs to outputs
        bus.write_byte_data(PCA_ADDR, REG_OUTPUT_1, p0)

    except Exception as e:
        log(f"INT error: {e}")

GPIO.add_event_detect(
    INT_PIN,
    GPIO.FALLING,
    callback=interrupt_cb,
    bouncetime=50
)

log("Interrupt handler armed")

# ================= MAIN LOOP =================
try:
    while True:
        time.sleep(5)
        log("Alive")

        # retry PCA detection if missing
        if not pca_ready and bus:
            pca_ready = pca_setup()

except KeyboardInterrupt:
    log("Keyboard exit")

except Exception as e:
    log(f"Fatal error: {e}")

finally:
    GPIO.cleanup()
    if bus:
        bus.close()
    log("Service stopped")
