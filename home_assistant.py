from config import *
from homeassistant_api import Client


def get_ha_climate_data():
    with Client(
        HA_SERVER_URL,
        HA_ACCESS_TOKEN
    ) as client:
        loft_temp = client.get_state(entity_id='sensor.loft_temp_temperature')
        loft_hum = client.get_state(entity_id='sensor.loft_temp_humidity')
        guest_temp = client.get_state(entity_id='sensor.guest_temp_temperature')
        guest_hum = client.get_state(entity_id='sensor.guest_temp_humidity')
        living_room_temp = client.get_state(entity_id='sensor.living_room_temp_temperature')
        living_room_hum = client.get_state(entity_id='sensor.living_room_temp_humidity')
        master_temp = client.get_state(entity_id='sensor.master_temp_temperature')
        master_hum = client.get_state(entity_id='sensor.master_temp_humidity')
        laundry_temp = client.get_state(entity_id='sensor.titan_water_valve_actuator_air_temperature')
        office_temp = client.get_state(entity_id='sensor.office_temp_temperature')
        office_hum = client.get_state(entity_id='sensor.office_temp_humidity')
        return {
            'temp_loft': loft_temp.state,
            'temp_living_room': living_room_temp.state,
            'temp_guest': guest_temp.state,
            'temp_master': master_temp.state,
            'temp_laundry': laundry_temp.state,
            'temp_office': office_temp.state,
            'hum_loft': loft_hum.state,
            'hum_guest': guest_hum.state,
            'hum_living_room': living_room_hum.state,
            'hum_master': master_hum.state,
            'hum_office': office_hum.state,
        }


# print(get_ha_climate_data())