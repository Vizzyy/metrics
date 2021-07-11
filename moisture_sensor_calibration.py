#!/usr/bin/python3

import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

max_value = 22700
min_value = 11216
diff_value = max_value - min_value

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)

while True:
    curr_value = chan.value
    curr_value -= min_value

    if curr_value > max_value:
        max_value = curr_value
    if curr_value < min_value:
        min_value = curr_value

    moisture_level = ((diff_value - curr_value) / diff_value) * 100

    print(f"Current: {curr_value} - Max: {max_value} - Min: {min_value} - Moisture Level: {moisture_level}%")
    time.sleep(1)

# Example Output:
# Current: 22608 - Max: 22608 - Min: 22608
# Current: 22464 - Max: 22608 - Min: 22464
# Current: 17248 - Max: 22608 - Min: 17248
# Current: 14416 - Max: 22608 - Min: 14416
# Current: 14128 - Max: 22608 - Min: 14128
# Current: 13808 - Max: 22608 - Min: 13808
