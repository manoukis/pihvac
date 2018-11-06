#!/usr/bin/python3
"""
Controlling AC, heat, humidifier, and dehumidifier
"""

import os
import sys
import RPi.GPIO as GPIO
import time
import smbus
import datetime
import sht31

## Config values -- @TCC Move these to a config file
# setpoints
TSP = 22  # temperature setpoint in 'C
HSP = 80  # RH setpoint in %

dT_h = 1  # delta T above to trigger AC
dT_l = 1  # delta T below to trigger Heat
dT_h2l = -0.5  # delta T above to turn off AC (hysteresis); <0 will overshoot
dT_l2h = -0.5  # delta T below to turn off Heat (hysteresis); <0 will overshoot


# Less mutable config values
POLLING_TIME = 10 # in seconds

PIN_AC = 17 # GPIO17
PIN_HEAT = 18 # GPIO18
PIN_HUMID = 27 # GPIO27
# pin 14 GND
PIN_DEHUMID = 22 # GPIO22


class Appliance:
    def __init__(self, pin):
        self.pin = pin
        self.state = None # 0=off, 1=on
        GPIO.setup(self.pin, GPIO.OUT)
        self.turn_off()
    
    def turn_on(self):
        GPIO.output(self.pin, GPIO.HIGH)
        self.state = 1
        
    def turn_off(self):
        GPIO.output(self.pin, GPIO.LOW)
        self.state = 0

    def is_on(self):
        return self.state == 1

# Timezone info just for outputting proper localtime format
utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
utc_offset = datetime.timedelta(seconds=-utc_offset_sec)

# Setup the GPIO pins
GPIO.setmode(GPIO.BCM) # GPIO.BCM to use pin numbers like 17 for GPIO17
GPIO.setwarnings(True)

ac = Appliance(PIN_AC)
heat = Appliance(PIN_HEAT)
humid = Appliance(PIN_HUMID)
dehumid = Appliance(PIN_DEHUMID)

# Setup the temperature/RH sensor
i2cbus = smbus.SMBus(1)
sht = sht31.SHT31(i2cbus)

try:
    humid.turn_on()
    while True:
        T,RH = sht.read()
        if T > TSP + dT_h:
            ac.turn_on()
            dehumid.turn_off()
        if ac.is_on() and T < TSP + dT_h2l:
            ac.turn_off()

        timestamp = datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()
        print(timestamp, T, RH, ac.is_on(), heat.is_on(), humid.is_on(), dehumid.is_on(), sep='\t')
        sys.stdout.flush()

        # delay until next polling cycle
        time.sleep(POLLING_TIME)

except KeyboardInterrupt:
    raise
finally:
    GPIO.cleanup()
