import requests
import json
from config import homebridge_auth_endpoint, homebridge_auth_payload, homebridge_accessories_endpoint

auth_response = json.loads(requests.post(homebridge_auth_endpoint, json=homebridge_auth_payload).text)
token = auth_response['access_token']


def get_sensor_state(unique_id, name=None):
  accessories_endpoint = f'{homebridge_accessories_endpoint}/{unique_id}'
  accessories = json.loads(requests.get(accessories_endpoint, headers={'Authorization': f'Bearer {token}'}).text)

  sensor_state = accessories['values']
  sensor_name = 'Sensor' if not name else name
  print(f'{sensor_name} state: {json.dumps(sensor_state, indent=2)}')
  return sensor_state

