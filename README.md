# pihvac
Raspberry pi control of temperature and humidity by switiching AC, heat, humidifier, and dehumidifier

- `pihvac.py` controls an AC, heater, humidifier, and dehumidifier to maintain a given temperature and RH.  Currently the setpoints and tolerances are just hard-coded as constantas at the top of the file.  It uses `sht31.py` to read temperature and RH from a SHT31 sensor attached to I2C and GIPO4.
- `sht31.py` is a module providing the SHT31 class for reading temperature & RH sensors.  It can deal with an arbitrary number of sensors attached to common I2C + one GPIO (select/enable) per sensor.
- `indoor_outdoor/read_sht31.py` is a simple standalone script for reading SHT31 temperature & RH sensors on a Raspberry Pi.  The `chamber_control` script for tracking a remote temperature calls runs this on a remote pi (via an ssh command) to get the current values.  It is adjusted to work on an old Raspberry Pi V1, while `sht31.py` wants the newer version of python available on new models.

There are various other files from trying out various interfaces (bokeh and cgi/www) as well as other cruft.  
Potentially of use is `smartgadgetBLEread.py` which reads data from a Sensitron SHT31 SmartGadget via bluetooth.
