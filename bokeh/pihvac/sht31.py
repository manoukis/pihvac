#!/usr/bin/env python3
# parts adapted from: http://www.pibits.net/code/raspberry-pi-sht31-sensor-example.php

import sys
import smbus2 as smbus
import RPi.GPIO as GPIO
import time
import errno


class SHT31:
    _default_address = 0x44
    _alt_address = 0x45

    def __init__(self, sm_bus, addr_gpio=None, i2c_address=None):
        """Setting addr_gpio overrides i2c_address to _alt_address for reads"""
        self.bus = sm_bus
        self.addr = i2c_address
        self.addr_gpio = addr_gpio
        self.T = None
        self.RH = None
        self.prev_T = None
        self.prev_RH = None
        if self.addr is None:
            self.addr = type(self)._default_address
        # if addr_gpio is set, use it to multiplex (reading at address 0x45)
        if self.addr_gpio is not None:
            self.addr = type(self)._alt_address
            GPIO.setup(self.addr_gpio, GPIO.OUT)
            GPIO.output(self.addr_gpio, GPIO.LOW)

    @staticmethod
    def _calculate_checksum(data, number_of_bytes=None):
        """CRC Checksum using the polynomial given in the SHT31 datasheet"""
        if number_of_bytes is None:
            number_of_bytes = len(data)
        # CRC
        POLYNOMIAL = 0x131  # //P(x)=x^8+x^5+x^4+1 = 100110001
        crc = 0xFF
        # calculates 8-Bit checksum with given polynomial
        for byteCtr in range(number_of_bytes):
            crc ^= (ord(chr(data[byteCtr])))
            for bit in range(8, 0, -1):
                if crc & 0x80:
                    crc = (crc << 1) ^ POLYNOMIAL
                else:
                    crc = (crc << 1)
        return crc

    def get_addr_gpio(self): return self.addr_gpio
    def get_T(self): return self.T
    def get_RH(self): return self.RH
    def get_prev_T(self): return self.prev_T
    def get_prev_RH(self): return self.prev_RH

    def read(self, rep='high', delay=None):
        # rep is 'repeatability'; basically quality but see the datasheet
        # High repeatablity measurement with clock stretching 0x2C 0x06 (default)
        # Med repeatablity measurement with clock stretching 0x2C 0x0D
        # Low repeatablity measurement with clock stretching 0x2C 0x10
        # delay is time between command and read (for measurement);
        #   delay=None will choose a value based on rep from the datasheed
        if rep.lower() == 'high':
            lsb = 0x06
            if delay is None: delay = 0.016
        elif rep.lower() == 'med':
            lsb = 0x0D
            if delay is None: delay = 0.007
        elif rep.lower() == 'low':
            lsb = 0x10
            if delay is None: delay = 0.002
        else:
            raise ValueError("rep must be 'high', 'med', or 'low'")
        # if using addr pin to enable read at 0x45, do so
        if self.addr_gpio is not None:
            GPIO.output(self.addr_gpio, GPIO.HIGH)
        # Send command
        self.bus.write_i2c_block_data(self.addr, 0x2C, [lsb])
        # delay
        time.sleep(delay)
        # Read data back from 0x00; 6 bytes [T MSB, T LSB, T CRC, RH MSB, RH LSB, RH CRC]
        data = self.bus.read_i2c_block_data(self.addr, 0x00, 6)
        # if using addr pin, switch back to 0x44 to free up 0x45
        if self.addr_gpio is not None:
            GPIO.output(self.addr_gpio, GPIO.LOW)
        # Check CRC
        if data[2] != self._calculate_checksum(data[0:2]):
            raise ConnectionError("CRC failed on I2C read from SHT31")
        if data[5] != self._calculate_checksum(data[3:5]):
            raise ConnectionError("CRC failed on I2C read from SHT31")
        # Save previous values (just in case)
        self.prev_T = self.T
        self.prev_RH = self.RH
        # Convert the data
        self.T = -45 + (175 * (data[0]*256 + data[1]) / 65535.0) # in 'C
        self.RH = 100 * (data[3]*256 + data[4]) / 65535.0
        return self.T, self.RH



def run_test():
    try: # outer try/except/finally to ensure cleanup
        # GPIO boilerplate
        GPIO.setmode(GPIO.BCM) # GPIO.BCM is numbers like 17 for GPIO17
        GPIO.setwarnings(True)

        ## Testing using address pin to select active device amoung many
        sht_list = [
            SHT31(smbus.SMBus(1), addr_gpio=4),
            SHT31(smbus.SMBus(1), addr_gpio=20),
            SHT31(smbus.SMBus(1), addr_gpio=21),
            ]

        for sht in sht_list:
            timefoo = time.time()
            print("Reading from SHT31 on pin", sht.get_addr_gpio())
            for i in range(10):
                try:
                    T, RH = sht.read(rep='high')
                    print(T, RH)
                except ConnectionError as e:
                    print("FAILED:", e)
                except OSError as e:
                    if e.errno == 121: # 121 is Remote I/O Error
                        print("FAILED:", e)
            print("Elapsed:", time.time()-timefoo)

#        for sht in sht_list:
#            timefoo = time.time()
#            print("Reading from SHT31 on pin", sht.get_addr_gpio(), ": Low repeatability")
#            for i in range(10):
#                try:
#                    T, RH = sht.read(rep='low')
#                    print(T, RH)
#                except ConnectionError as e:
#                    print("FAILED:", e)
#                except OSError as e:
#                    if e.errno == 121:
#                        print("FAILED:", e)
#            print("Elapsed:", time.time()-timefoo)

    finally: # ensure cleanup
        GPIO.cleanup()

## Main loop hook for running as a script
if __name__ == "__main__":
    sys.exit(run_test())

