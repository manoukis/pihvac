#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Controlling AC, heat, humidifier, and dehumidifier

PIN_AC = 11 # GPIO17
PIN_HEAT = 12 # GPIO18
PIN_DEHUMID = 13 # GPIO27
# pin 14 GND
PIN_HUMID = 15 # GPIO22

GPIO.setmode(GPIO.BOARD) # GPIO.BCM would be pin numbers like 17 for GPIO17
GPIO.setwarnings(True)

pin = PIN_AC

GPIO.setup(pin, GPIO.OUT)

try:
    for i in range(5):
        GPIO.output(pin, GPIO.LOW)
        time.sleep(1.0)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.5)

except KeyboardInterrupt:
    raise
finally:
    GPIO.cleanup()
