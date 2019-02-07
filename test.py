#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Controlling AC, heat, humidifier, and dehumidifier

PIN_AC = 19 # pin 35, GPIO19
PIN_HEAT = 16 # pin 36, GPIO16
PIN_DEHUMID = 26 # pin 37, GPIO26
PIN_HUMID = 20 # pin 38, GPIO20
PIN_FAN = 13 # pin 33, GPIO13
PIN_LIGHT = 21 # pin 40, GPIO21

GPIO.setmode(GPIO.BCM) # GPIO.BCM is pin numbers like 17 for GPIO17
GPIO.setwarnings(True)

pin = PIN_AC

try:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(10)

#try:
#    for i in range(5):
#        GPIO.output(pin, GPIO.LOW)
#        time.sleep(1.0)
#        GPIO.output(pin, GPIO.HIGH)
#        time.sleep(0.5)

except KeyboardInterrupt:
    raise
finally:
    GPIO.cleanup()
