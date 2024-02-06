from config import *
import requests
import json
from datetime import datetime

BASE_URL = 'https://api.flumewater.com'
headers = {
    "accept": "application/json",
    "content-type": "application/json"
}
access_token = None
refresh_token = None


def get_oauth_token():
    oauth_url = f'{BASE_URL}/oauth/token?envelope=true'
    oauth_token_payload = { 
        "grant_type": "password", # must be password
        "client_id": FLUME_CLIENT_ID,
        "client_secret": FLUME_CLIENT_SECRET,
        "username": FLUME_CLIENT_USERNAME,
        "password": FLUME_CLIENT_PASSWORD   
    }
    response = requests.post(oauth_url, json=oauth_token_payload, headers=headers)
    # print(vars(response))
    return response.text


def read_from_tokens_file():
    global access_token, refresh_token
    try:
        with open('./tokens.json', 'r') as tokens_file:
            contents = tokens_file.read()
            contents = json.loads(contents)
            # print(contents)
            access_token = contents['access_token']
            refresh_token = contents['refresh_token']
            # print('loaded tokens from file!')
            return True
    except Exception as e:
        print(f'ERROR READING TOKENS FILE - {type(e).__name__} - {e}')
    return False


def write_to_tokens_file():
    global access_token, refresh_token
    try:
        with open('./tokens.json', "w") as tokens_file:
            contents = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            # print(contents)
            tokens_file.write(json.dumps(contents, indent=2))
            return True
    except Exception as e:
        print(f'ERROR WRITING TOKENS FILE - {type(e).__name__} - {e}')
    return False


def check_token_valid():
    url = f'{BASE_URL}/me'
    bearer = headers.copy()
    bearer['Authorization'] = f'Bearer {access_token}'
    response = requests.get(url, headers=bearer)
    response = json.loads(response.text)
    # print(json.dumps(response, indent=2))
    if response['http_code'] == 200:
        # print(f'token valid!')
        return True
    else:
        print(f'check_token_valid: token invalid!')
        return False
    

def get_devices():
    url = f'{BASE_URL}/me/devices'
    bearer = headers.copy()
    bearer['Authorization'] = f'Bearer {access_token}'
    response = requests.get(url, headers=bearer)
    return json.loads(response.text)


def query_data(user_id, device_id, payload):
    url = f'{BASE_URL}/users/{user_id}/devices/{device_id}/query'
    bearer = headers.copy()
    bearer['Authorization'] = f'Bearer {access_token}'
    response = requests.request("POST", url, json=payload, headers=bearer)
    return json.loads(response.text)


def get_current_monthly_usage():
    devices = get_devices()
    query = {
        "queries": [
            {
            "bucket": "MON",
            "since_datetime": f"{datetime.now().year}-{datetime.now().month:02d}-01 00:00:00",
            "operation": "sum",
            "request_id": "get_current_monthly_usage"
            }
        ]
    }
    # print(f'devices: {devices}')
    # print(f'query: {query}')

    result = query_data(devices['data'][0]['user_id'], devices['data'][0]['id'], query)
    # print(f'get_current_monthly_usage: {result}')

    usage_gallons = result['data'][0]['get_current_monthly_usage'][0]['value']
    # print(f'usage_gallons: {usage_gallons}')
    return usage_gallons


if not read_from_tokens_file() or not check_token_valid():
    api_credentials = json.loads(get_oauth_token())
    access_token = api_credentials['data'][0]['access_token']
    refresh_token = api_credentials['data'][0]['refresh_token']
    write_to_tokens_file()
    


print(get_current_monthly_usage())

