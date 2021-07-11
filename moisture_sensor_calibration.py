#!/usr/bin/python3

import time
import board
import busio
from config import *
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

max_value = moisture_calibration_max
min_value = moisture_calibration_min
diff_value = max_value - min_value

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)

while True:
    curr_value = chan.value

    moisture_level = 100 - (((curr_value - min_value) / diff_value) * 100)

    print(f"Current: {curr_value} - Max: {max_value} - Min: {min_value} - Moisture Level: {moisture_level}%")
    time.sleep(1)

# Example Output:
# Current: 22592 - Max: 22592 - Min: 11280 - Moisture Level: 0.0%
# Current: 22592 - Max: 22592 - Min: 11280 - Moisture Level: 0.0%
# Current: 22592 - Max: 22592 - Min: 11280 - Moisture Level: 0.0%
# Current: 14592 - Max: 22592 - Min: 11280 - Moisture Level: 70.72135785007072%
# Current: 13648 - Max: 22592 - Min: 11280 - Moisture Level: 79.06647807637907%
# Current: 12656 - Max: 22592 - Min: 11280 - Moisture Level: 87.83592644978783%
# Current: 12016 - Max: 22592 - Min: 11280 - Moisture Level: 93.4936350777935%
# Current: 11520 - Max: 22592 - Min: 11280 - Moisture Level: 97.87835926449787%
# Current: 11344 - Max: 22592 - Min: 11280 - Moisture Level: 99.43422913719944%
# Current: 11344 - Max: 22592 - Min: 11280 - Moisture Level: 99.43422913719944%
# Current: 11488 - Max: 22592 - Min: 11280 - Moisture Level: 98.16124469589816%
# Current: 12416 - Max: 22592 - Min: 11280 - Moisture Level: 89.95756718528996%
# Current: 14032 - Max: 22592 - Min: 11280 - Moisture Level: 75.67185289957567%
# Current: 19808 - Max: 22592 - Min: 11280 - Moisture Level: 24.611032531824605%
# Current: 22592 - Max: 22592 - Min: 11280 - Moisture Level: 0.0%
# Current: 22592 - Max: 22592 - Min: 11280 - Moisture Level: 0.0%
# Current: 22592 - Max: 22592 - Min: 11280 - Moisture Level: 0.0%

