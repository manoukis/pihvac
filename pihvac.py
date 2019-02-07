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

## Config values -- Should probably move these to a config file
LIGHT_ON_TIME = "6:00"
LIGHT_OFF_TIME = "18:00"

# setpoints
TSP = 24.5  # temperature setpoint in 'C
HSP = 70  # RH setpoint in %

dT_h = 0.5  # delta T above to trigger AC
dT_l = 0.5  # delta T below to trigger Heat
dT_h2l = -0.5*dT_l  # delta T above to turn off AC (hysteresis); <0 will overshoot
dT_l2h = -0.5*dT_h  # delta T below to turn off Heat (hysteresis); <0 will overshoot

dH_h = 5  # delta H above to trigger Humid
dH_l = 5  # delta H below to trigger Dehumid
dH_h2l = -0.5*dH_l  # delta H above to turn off Humid (hysteresis); <0 will overshoot
dH_l2h = -0.5*dH_h  # delta H below to turn off Dehumid (hysteresis); <0 will overshoot

# Less mutable config values
POLLING_TIME = 60 # in seconds
READ_FAILED_POLLING_TIME = 1 # delay before retrying if a T/RH read failed

PIN_SHT31 = 4 # GPIO4 ; address pin for SHT31

PIN_AC = 19 # pin 35, GPIO19
PIN_HEAT = 16 # pin 36, GPIO16
PIN_DEHUMID = 26 # pin 37, GPIO26
PIN_HUMID = 20 # pin 38, GPIO20
PIN_FAN = 13 # pin 33, GPIO13
PIN_LIGHT = 21 # pin 40, GPIO21

# TODO add fan control

class Appliance:
    def __init__(self, pin):
        self.pin = pin
        self.state = None # 0=off, 1=on
        GPIO.setup(self.pin, GPIO.OUT)
        self.turn_off()

    def turn_on(self):
        #print(self.pin, "on")
        GPIO.output(self.pin, GPIO.HIGH)
        self.state = 1

    def turn_off(self):
        #print(self.pin, "off")
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
light = Appliance(PIN_LIGHT)

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

        ## Light ##
        nowtime = datetime.datetime.now()
        tmp = datetime.datetime.strptime(LIGHT_ON_TIME, "%H:%M")
        ontime = nowtime.replace(hour=tmp.hour, minute=tmp.minute)
        tmp = datetime.datetime.strptime(LIGHT_OFF_TIME, "%H:%M")
        offtime = nowtime.replace(hour=tmp.hour, minute=tmp.minute)
        if nowtime > ontime and nowtime < offtime:
            light.turn_on()
        else:
            light.turn_off()

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
        #if H > HSP + dH_h:
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
