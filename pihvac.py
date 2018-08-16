#!/usr/bin/python3
"""
Controlling AC, heat, humidifier, and dehumidifier
"""

import RPi.GPIO as GPIO
import time
import smbus
import sht31

## Config values -- @TCC Move these to a config file
# setpoints
TSP = 24  # temperature setpoint in 'C
HSP = 80  # RH setpoint in %

dT_h = 2  # delta T above to trigger AC
dT_l = 2  # delta T below to trigger Heat
dT_h2l = 1  # delta T above to turn off AC (hysteresis)
dT_l2h = 1  # delta T below to turn off Heat (hysteresis)


# Less mutable config values
PIN_AC = 11 # GPIO17
PIN_HEAT = 12 # GPIO18
PIN_HUMID = 13 # GPIO27
# pin 14 GND
PIN_DEHUMID = 15 # GPIO22


# Setup the GPIO pins
GPIO.setmode(GPIO.BOARD) # GPIO.BCM would be pin numbers like 17 for GPIO17
GPIO.setwarnings(True)
for pin in [PIN_AC, PIN_HEAT, PIN_HUMID, PIN_DEHUMID]:
    GPIO.setup(pin, GPIO.OUT)

# Setup the temperature/RH sensor
i2cbus = smbus.SMBus(1)
sht = sht31.SHT31(i2cbus)

try:
    for i in range(100):
        T,RH = sht.read()
        print(T,RH)
        GPIO.output(PIN_AC, GPIO.HIGH)
        time.sleep(1.0)
        GPIO.output(PIN_AC, GPIO.LOW)
        time.sleep(1.0)

except KeyboardInterrupt:
    raise
finally:
    GPIO.cleanup()
