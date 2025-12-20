import board
import busio
import adafruit_pcf8575
import time

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

# PCF8575 at address 0x27
pcf = adafruit_pcf8575.PCF8575(i2c, 0x27)

# Initialize all pins as outputs if needed (PCF8575 defaults to input)
for pin in range(16):
    # some libraries don't require setup; just write directly
    pcf.output(pin, False)  # set LOW

# Toggle pins
while True:
    for pin in range(16):
        pcf.output(pin, True)  # HIGH
        time.sleep(0.5)
        pcf.output(pin, False)  # LOW
        time.sleep(0.5)
