# pihvac
Raspberry pi control of temperature and humidity by switiching AC, heat, humidifier, and dehumidifier

- `pihvac.py` controls an AC, heater, humidifier, and dehumidifier to maintain a given temperature and RH.  Currently the setpoints and tolerances are just hard-coded as constantas at the top of the file.  It uses `sht31.py` to read temperature and RH from a SHT31 sensor attached to I2C and GIPO4.
- `sht31.py` is a module providing the SHT31 class for reading temperature & RH sensors.  It can deal with an arbitrary number of sensors attached to common I2C + one GPIO (select/enable) per sensor.
- `indoor_outdoor/read_sht31.py` is a simple standalone script for reading SHT31 temperature & RH sensors on a Raspberry Pi.  The `chamber_control` script for tracking a remote temperature calls runs this on a remote pi (via an ssh command) to get the current values.  It is adjusted to work on an old Raspberry Pi V1, while `sht31.py` wants the newer version of python available on new models.

There are various other files from trying out various interfaces (bokeh and cgi/www) as well as other cruft.  
Potentially of use is `smartgadgetBLEread.py` which reads data from a Sensitron SHT31 SmartGadget via bluetooth.


## pihvac.py

nominal output are tab separated rows like:  
```2019-02-07T12:26:09.633537-10:00        24.96   24.50   70.46   70.00   False  False    False   False   True```
- Timestamp
- Temperature last sensor read
- Temperature setpoint
- Relative humidity last sensor read
- Relative humidity setpoint
- AC is on?
- Heat is on?
- Humidifier is on?
- Dehumidifier is on?
- Light is on?

## Hardware

SHT31 modules are connected to a Pi SMBUS using pins:  
- 1 : 3v3
- 3 : SDA1 I2C
- 5 : SCL1 I2C
- 7* : GPIO4 (or any other GPIO) connected to the SHT31 addr pin
**Multiple SHT31 modules can share the same connections with the exception of this GPIO pin.**
- 9 : Ground

The Pi in the insectary container has 6 GPIO and 2 Ground connections wired over to the powertails/relays.
Those are pins 33 to 40:
- 33 : GPIO13 : Orange : Unused (labeled Fan)
- 34 : Ground : Orange Stripe
- 35 : GPIO19 : Green : **AC**
- 36 : GPIO16 : Green Stripe : **Heater**
- 37 : GPIO26 : Brown : **Dehumidifier**
- 38 : GPIO20 : Brown Stripe : **Humidifer**
- 39 : Ground : Blue
- 40 : GPIO21 : Blue Stripe : **Light**

