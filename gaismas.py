from pcf8575 import PCF8575
import time

PCF_ADDR = 0x27
pcf = PCF8575(PCF_ADDR)  # just address

while True:
    for pin in range(16):
        pcf.digital_write(pin, 0)  # turn relay ON
        print(f"Relay {pin+1} ON")
        time.sleep(0.5)

        pcf.digital_write(pin, 1)  # turn relay OFF
        print(f"Relay {pin+1} OFF")
        time.sleep(0.2)
