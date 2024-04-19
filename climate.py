def get_climate_measurements():
    import board
    import adafruit_dht

    try:
        sensor = adafruit_dht.DHT22(board.D4, use_pulseio=False)
        temperature = sensor.temperature
        humidity = sensor.humidity
        return humidity, temperature
    except Exception as error:
        sensor.exit()
        print(f'{type(error).__name__} - Failed to get climate reading - {error}')

    return None

