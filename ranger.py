import RPi.GPIO as GPIO
import time

SIG_PIN = 16  # BCM 23

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(SIG_PIN, GPIO.OUT)

def measure_distance():
    GPIO.output(SIG_PIN, GPIO.LOW)
    time.sleep(0.002)
    GPIO.output(SIG_PIN, GPIO.HIGH)
    time.sleep(0.01)
    GPIO.output(SIG_PIN, GPIO.LOW)

    GPIO.setup(SIG_PIN, GPIO.IN)
    
    start_time = time.time()
    while GPIO.input(SIG_PIN) == 0:
        start_time = time.time()

    while GPIO.input(SIG_PIN) == 1:
        end_time = time.time()

    duration = end_time - start_time
    distance_cm = duration * 17150
    return round(distance_cm, 2)

try:
    setup()
    while True:
        dist = measure_distance()
        print(f"Distance: {dist} cm")
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
