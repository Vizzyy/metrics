def get_climate_measurements():
    import Adafruit_DHT

    sensor = Adafruit_DHT.DHT22  # DHT22 Temperature/Humidity Sensor
    pin = 4  # Pi data pin.

    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    if humidity is not None and humidity < 100 and temperature is not None and temperature < 38:
        return humidity, temperature
    else:
        print('Failed to get climate reading.')
