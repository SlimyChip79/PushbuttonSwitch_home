#!/usr/bin/env python3
from pcf8575 import PCF8575
import time

PCF_ADDR = 0x27
pcf = PCF8575(1, PCF_ADDR)  # bus 1

# setup all 16 pins as outputs
for i in range(16):
    pcf.setup(i, pcf.OUT)
    pcf.write(i, 1)  # 1 = off (active-low)

try:
    while True:
        for i in range(16):
            # turn ON relay
            pcf.write(i, 0)
            print(f"Relay {i+1} ON")
            time.sleep(0.5)

            # turn OFF relay
            pcf.write(i, 1)
            print(f"Relay {i+1} OFF")
            time.sleep(0.2)

except KeyboardInterrupt:
    print("Stopping, turning all relays off...")
    for i in range(16):
        pcf.write(i, 1)
