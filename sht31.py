#!/usr/bin/python3
# from: http://www.pibits.net/code/raspberry-pi-sht31-sensor-example.php

import sys
import smbus
import time


class SHT31:
    def __init__(self, sm_bus, i2c_address=0x44):
        self.bus = sm_bus
        self.addr = i2c_address
        self.T = None
        self.RH = None
        self.prev_T = None
        self.prev_RH = None

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
        # Send command
        self.bus.write_i2c_block_data(self.addr, 0x2C, [lsb])
        # delay
        time.sleep(delay)
        # Read data back from 0x00; 6 bytes [T MSB, T LSB, T CRC, RH MSB, RH LSB, RH CRC]
        data = self.bus.read_i2c_block_data(self.addr, 0x00, 6)
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
    # Get I2C bus
    bus = smbus.SMBus(1)

    sht = SHT31(bus)
    for i in range(10):
        T, RH = sht.read(rep='high')
        print(T, RH)

##print(" ".join([hex(_) for _ in data]))
# Temperature checksum
#crc = _calculate_checksum(data[0:2], 2)
#print(hex(crc))
## Humidity checksum
#crc = _calculate_checksum(data[3:5], 2)
#print(hex(crc))

## Main loop hook for running as a script
if __name__ == "__main__":
    sys.exit(run_test())

