#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Controlling AC, heat, humidifier, and dehumidifier

PIN_AC = 11 # GPIO17
PIN_HEAT = 12 # GPIO18
PIN_HUMID = 13 # GPIO27
# pin 14 GND
PIN_DEHUMID = 15 # GPIO22

GPIO.setmode(GPIO.BOARD) # GPIO.BCM would be pin numbers like 17 for GPIO17
GPIO.setwarnings(True)

GPIO.setup(PIN_AC, GPIO.OUT)

try:
    for i in range(100):
        GPIO.output(PIN_AC, GPIO.HIGH)
        time.sleep(1.0)
        GPIO.output(PIN_AC, GPIO.LOW)
        time.sleep(1.0)

except KeyboardInterrupt:
    raise
finally:
    GPIO.cleanup()
