#!/usr/bin/python3

import sys
import RPi.GPIO as GPIO
import smbus
from sht31 import SHT31

PIN_ALIASES = {'in':4, 'out':17}

pin = None
if len(sys.argv) > 1:
    if sys.argv[1].isdigit(): # a simple int, assume it is the pin number
        pin = int(sys.argv[1])
    else:
        if sys.argv[1] not in PIN_ALIASES:
            print("ERROR: Valid PIN aliases are:",PIN_ALIASES, file=sys.stderr)
            sys.exit(1)
        pin = PIN_ALIASES[sys.argv[1]]

if pin is None:
    print("Must provide pin number or alias as argument!", file=sys.stderr)
    sys.exit(1)

try: # outer try/except/finally to ensure cleanup
    # GPIO boilerplate
    GPIO.setmode(GPIO.BCM) # GPIO.BCM is numbers like 17 for GPIO17
    GPIO.setwarnings(True)

    sht = SHT31(smbus.SMBus(1), addr_gpio=pin)

#    print("Reading from SHT31 on pin", sht.get_addr_gpio(), file=sys.stderr)
    # read with nofail
    T, RH = sht.read(rep='high', nofail=True)
#    print(sht.get_read_time(), T, RH,
#          sht.get_last_read_error(),
#          sht.get_prev_read_time(),
#          sht.get_prev_T(), sht.get_prev_RH(), file=sys.stderr)

    print("{0:0.1f}\t{1:0.1f}".format(T, RH))

## Code example for reading without nofail set (handling exceptions here)
#                try:
#                    T, RH = sht.read(rep='high')
#                    print(T, RH)
#                except ConnectionError as e:
#                    print("FAILED:", e)
#                except OSError as e:
#                    if e.errno == 121: # 121 is Remote I/O Error
#                        print("FAILED:", e)

finally: # ensure cleanup
    GPIO.cleanup()
