import time
import board
import busio
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_mcp230xx.digital_inout import DigitalInOut
from adafruit_pcf8575 import PCF8575

i2c = busio.I2C(board.SCL, board.SDA)
time.sleep(1)

mcp = MCP23017(i2c, address=0x20)
pcf = PCF8575(i2c, address=0x26)

buttons = [DigitalInOut(mcp, i) for i in range(16)]
for b in buttons:
    b.switch_to_input()

pcf.write_gpio(0xFFFF)
time.sleep(0.2)

states = [False]*16

while True:
    out = 0xFFFF
    for i, b in enumerate(buttons):
        if b.value and not states[i]:
            states[i] = not states[i]
        if states[i]:
            out &= ~(1 << i)
    pcf.write_gpio(out)
    print([b.value for b in buttons])
    time.sleep(0.05)
