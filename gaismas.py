import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

PIN = 17
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Reading GPIO17 once per second (Ctrl+C to exit)")

try:
    while True:
        state = GPIO.input(PIN)
        print(f"{time.strftime('%H:%M:%S')} | GPIO17 = {state}", flush=True)
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    GPIO.cleanup()
    print("Clean exit")
