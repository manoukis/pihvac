#!/usr/bin/env python3
"""
Controlling AC, heat, humidifier, and dehumidifier
"""

import os
import sys
import RPi.GPIO as GPIO
import time
import smbus2 as smbus
import datetime
import sht31

## Config values -- @TCC Move these to a config file
# setpoints
TSP = 23  # temperature setpoint in 'C
HSP = 80  # RH setpoint in %

dT_h = 1  # delta T above to trigger AC
dT_l = 1  # delta T below to trigger Heat
dT_h2l = -0.25  # delta T above to turn off AC (hysteresis); <0 will overshoot
dT_l2h = -0.25  # delta T below to turn off Heat (hysteresis); <0 will overshoot

dH_h = 5  # delta H above to trigger Humid
dH_l = 5  # delta H below to trigger Dehumid
dH_h2l = 0  # delta H above to turn off Humid (hysteresis); <0 will overshoot
dH_l2h = 0  # delta H below to turn off Dehumid (hysteresis); <0 will overshoot

# Less mutable config values
POLLING_TIME = 10 # in seconds
READ_FAILED_POLLING_TIME = 1 # delay before retrying if a T/RH read failed

PIN_SHT31 = 4 # GPIO4 ; address pin for SHT31

PIN_AC = 17 # GPIO17
PIN_HEAT = 18 # GPIO18
PIN_HUMID = 27 # GPIO27
# pin 14 GND
PIN_DEHUMID = 22 # GPIO22

# @TCC TODO add light and fan control

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
sht = sht31.SHT31(smbus.SMBus(1), addr_gpio=PIN_SHT31)

try:
    while True:
        T, H = sht.read(rep='high', nofail=True)
        if sht.get_last_read_error() is not None: # read failed, delay and try again
            # @TCC NEED TO TRIGGER SENDING AN ALARM HERE
            print("T/RH READ FAILED")
            time.sleep(READ_FAILED_POLLING_TIME)
            continue

        ## AC ##
        if T > TSP + dT_h:
            ac.turn_on()
            dehumid.turn_off()
        if T < TSP + dT_h2l:
            ac.turn_off()
        ## Heat ##
        if T < TSP - dT_l:
            heat.turn_on()
            dehumid.turn_off()
        if T > TSP - dT_l2h:
            heat.turn_off()
        ## Dehumid ## @TCC not certain about interplay with ac and heat
        if not ac.is_on() and not heat.is_on() and H > HSP + dH_h:
            dehumid.turn_on()
        if H < HSP + dH_h2l:
            dehumid.turn_off()
        ## Humid ## @TCC not certain about interplay with ac and heat
        if H < HSP - dH_l:
            humid.turn_on()
        if H > HSP - dH_l2h:
            humid.turn_off()

        timestamp = datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()
        print(timestamp, "{:0.2f}\t{:0.2f}".format(T,TSP),
                "{:0.2f}\t{:0.2f}".format(H,HSP),
                ac.is_on(), heat.is_on(), humid.is_on(), dehumid.is_on(), sep='\t')
        sys.stdout.flush()

        # delay until next polling cycle
        time.sleep(POLLING_TIME)

except KeyboardInterrupt:
    raise
finally:
    GPIO.cleanup()
