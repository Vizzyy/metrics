from config import *
from homeassistant_api import Client


def get_ha_climate_data():
    with Client(
        HA_SERVER_URL,
        HA_ACCESS_TOKEN
    ) as client:
        temp_loft = client.get_state(entity_id='sensor.loft_temp_temperature')
        hum_loft = client.get_state(entity_id='sensor.loft_temp_humidity')
        temp_guest = client.get_state(entity_id='sensor.guest_temp_temperature')
        hum_guest = client.get_state(entity_id='sensor.guest_temp_humidity')
        temp_living_room = client.get_state(entity_id='sensor.living_room_temp_temperature')
        temp_lr_nest = client.get_state(entity_id='sensor.downstairs_thermostat_current_temperature')
        hum_lr_nest = client.get_state(entity_id='sensor.downstairs_thermostat_current_humidity')
        hum_living_room = client.get_state(entity_id='sensor.living_room_temp_humidity')
        temp_master = client.get_state(entity_id='sensor.master_temp_temperature')
        hum_master = client.get_state(entity_id='sensor.master_temp_humidity')
        temp_laundry = client.get_state(entity_id='sensor.titan_water_valve_actuator_air_temperature')
        temp_office = client.get_state(entity_id='sensor.office_temp_temperature')
        hum_office = client.get_state(entity_id='sensor.office_temp_humidity')
        temp_attic = client.get_state(entity_id='sensor.atticpuck_temperature')
        hum_attic = client.get_state(entity_id='sensor.atticpuck_humidity')
        temp_loft_nest = client.get_state(entity_id='sensor.loft_temperature')
        temp_master_nest = client.get_state(entity_id='sensor.master_bedroom_temperature')
        water_usage_daily = client.get_state(entity_id='sensor.water_usage_daily')
        water_usage_weekly = client.get_state(entity_id='sensor.water_usage_weekly')
        water_usage_monthly = client.get_state(entity_id='sensor.water_usage_monthly')
        return {
            'temp_loft': temp_loft.state,
            'temp_living_room': temp_living_room.state,
            'temp_guest': temp_guest.state,
            'temp_master': temp_master.state,
            'temp_laundry': temp_laundry.state,
            'temp_office': temp_office.state,
            'temp_loft_nest': temp_loft_nest.state,
            'temp_master_nest': temp_master_nest.state,
            'temp_lr_nest': temp_lr_nest.state,
            'temp_attic': temp_attic.state,
            'hum_loft': hum_loft.state,
            'hum_guest': hum_guest.state,
            'hum_living_room': hum_living_room.state,
            'hum_master': hum_master.state,
            'hum_office': hum_office.state,
            'hum_lr_nest': hum_lr_nest.state,
            'hum_attic': hum_attic.state,
            'water_usage_daily': water_usage_daily.state if water_usage_daily.state != 'unknown' else 0,
            'water_usage_weekly': water_usage_weekly.state if water_usage_weekly.state != 'unknown' else 0,
            'water_usage_monthly': water_usage_monthly.state if water_usage_monthly.state != 'unknown' else 0,
        }


# print(get_ha_climate_data())