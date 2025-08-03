import RPi.GPIO as GPIO
import time

# Use BCM numbering (GPIO16 = pin 36 on Pi)
SIG_PIN = 16

def setup_sensor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SIG_PIN, GPIO.OUT)
    GPIO.output(SIG_PIN, GPIO.LOW)
    time.sleep(0.05)  # Allow sensor to settle

def measure_distance():
    # Set SIG as output to send trigger pulse
    GPIO.setup(SIG_PIN, GPIO.OUT)
    GPIO.output(SIG_PIN, GPIO.LOW)
    time.sleep(0.002)
    GPIO.output(SIG_PIN, GPIO.HIGH)
    time.sleep(0.01)  # 10 microseconds pulse
    GPIO.output(SIG_PIN, GPIO.LOW)

    # Set SIG as input to receive echo
    GPIO.setup(SIG_PIN, GPIO.IN)

    # Wait for echo start
    timeout = time.time() + 0.04  # 40ms timeout
    while GPIO.input(SIG_PIN) == 0:
        if time.time() > timeout:
            return -1
    start = time.time()

    # Wait for echo end
    timeout = time.time() + 0.04
    while GPIO.input(SIG_PIN) == 1:
        if time.time() > timeout:
            return -1
    end = time.time()

    duration = end - start
    distance_cm = duration * 17150  # Speed of sound calculation
    return round(distance_cm, 2)

def check_occupied():
    distance = measure_distance()
    if distance == -1:
        return False  # sensor error or no reading
    return 10 < distance < 300

def cleanup_sensor():
    GPIO.cleanup()
    return