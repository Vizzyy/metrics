import requests
from config import nest_refresh_token_query_params, nest_device_project_id

access_token = None


def convert_to_f(c):
    return c * (9 / 5) + 32


def get_access_token():
    print(f'Getting new nest access token...')
    # Get new oauth token using existing refresh token
    r = requests.post('https://www.googleapis.com/oauth2/v4/token', params=nest_refresh_token_query_params)
    response_body = r.json()
    if 'access_token' in response_body:
        token = response_body['access_token']
        # print(f'New token: {token}')
    else:
        raise (Exception(f'NEST - No Access Token available in oauth response. Response body: {response_body}'))

    return token


def get_nest_data():
    global access_token
    nest_data = []
    try:
        if not access_token:
            access_token = get_access_token()

        # print(f'get_nest_data: {access_token}')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        # Get device(s)
        r = requests.get(
            f'https://smartdevicemanagement.googleapis.com/v1/enterprises/{nest_device_project_id}/devices',
            headers=headers)
        response_body = r.json()
        # print(f'Devices response: {response_body}')
        try:
            devices = response_body['devices']
        except Exception as ex:
            # TODO: Check response to confirm token expiration message. Token appears to expire after 1hr
            #  response_body: {'error': {'code': 401, 'message': 'Request had invalid authentication credentials.
            #  Expected OAuth 2 access token, login cookie or other valid authentication credential. See
            #  https://developers.google.com/identity/sign-in/web/devconsole-project.', 'status': 'UNAUTHENTICATED'}}
            print(f'Device Data was not returned - {type(ex).__name__} - {ex} - response_body: {response_body}')
            access_token = get_access_token()
            raise ex

        for device in devices:
            # print(json.dumps(device, indent=4, sort_keys=True))

            traits = {
                'display_name': device['parentRelations'][0]['displayName'],
                'fan_on': 0 if device['traits']['sdm.devices.traits.Fan']['timerMode'] == 'OFF' else 1,
                'humidity': device['traits']['sdm.devices.traits.Humidity']['ambientHumidityPercent'],
                'temperature_ambient_c': device['traits']['sdm.devices.traits.Temperature'][
                    'ambientTemperatureCelsius'],
                'temperature_ambient_f': convert_to_f(
                    device['traits']['sdm.devices.traits.Temperature']['ambientTemperatureCelsius']
                ),
                'mode_heat': 1 if device['traits']['sdm.devices.traits.ThermostatMode']['mode'] == 'HEAT' else 0,
                'mode_cool': 1 if device['traits']['sdm.devices.traits.ThermostatMode']['mode'] == 'COOL' else 0,
                'mode_heatcool': 1 if device['traits']['sdm.devices.traits.ThermostatMode'][
                                          'mode'] == 'HEATCOOL' else 0,
                'mode_off': 1 if device['traits']['sdm.devices.traits.ThermostatMode']['mode'] == 'OFF' else 0,
                'hvac_cooling': 1 if device['traits']['sdm.devices.traits.ThermostatHvac'][
                                         'status'] == 'COOLING' else 0,
                'hvac_heating': 1 if device['traits']['sdm.devices.traits.ThermostatHvac'][
                                         'status'] == 'HEATING' else 0,
                'hvac_off': 1 if device['traits']['sdm.devices.traits.ThermostatHvac']['status'] == 'OFF' else 0,
            }

            for set_point in device['traits']['sdm.devices.traits.ThermostatTemperatureSetpoint'].keys():
                traits['temperature_set_point_c'] = \
                    device['traits']['sdm.devices.traits.ThermostatTemperatureSetpoint'][set_point]
                traits['temperature_set_point_f'] = convert_to_f(
                    device['traits']['sdm.devices.traits.ThermostatTemperatureSetpoint'][set_point]
                )
                traits['set_point_cool'] = 1 if set_point == 'coolCelsius' else 0
                traits['set_point_heat'] = 1 if set_point == 'heatCelsius' else 0

            nest_data.append(traits)
            # print(json.dumps(traits, indent=4, sort_keys=True))
    except Exception as e:
        print(f'{type(e).__name__} - {e}')

    return nest_data
