import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

PIN = 17
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Reading GPIO17 (Ctrl+C to exit)")

try:
    while True:
        state = GPIO.input(PIN)
        print(f"GPIO17 = {state}")
        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
    print("Clean exit")
