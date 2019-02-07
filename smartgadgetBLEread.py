#!/usr/bin/env python

import sys
import os
import time
import struct
import pygatt

# To discover mac addresses of nearby (on) devices:
# sudo hcitool lescan

#MACADDR = "CA:34:B1:3D:25:42"
MACADDR = "C4:29:BF:E7:CA:98"


ADDRESS_TYPE = pygatt.BLEAddressType.random
TEMPERATURE_UUID = "00002235-b38d-4985-720e-0f993a68ee41"
HUMIDITY_UUID = "00001235-b38d-4985-720e-0F993a68ee41"
BATTERY_UUID = "2A19"


adapter = pygatt.GATTToolBackend()
adapter.start()

device = adapter.connect(MACADDR, address_type=ADDRESS_TYPE, timeout=10)
print("connected", MACADDR)

for i in range(1000):

    temp = device.char_read(TEMPERATURE_UUID)
    tempf = struct.unpack('<f',temp)[0]
    print("read temp : {:.2f}".format(tempf))

    humi = device.char_read(HUMIDITY_UUID)
    humif = struct.unpack('<f',humi)[0]
    print("read humi : {:.2f}".format(humif))

    batt = device.char_read(BATTERY_UUID)
    print("read batt : {:d}".format(batt[0]))

    time.sleep(1)

device.disconnect()
adapter.stop()
