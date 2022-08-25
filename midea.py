from config import MIDEA_IP, MIDEA_TOKEN, MIDEA_KEY
from midea_beautiful import appliance_state
from nest import convert_to_f


def get_midea_data():
    appliance = appliance_state(address=MIDEA_IP, token=MIDEA_TOKEN, key=MIDEA_KEY)
    data = vars(appliance.state)

    # [print(key, " = ", data[key]) for key in data.keys()]

    midea_data = {
        'indoor_temperature': convert_to_f(data["_indoor_temperature"]),
        'outdoor_temperature': convert_to_f(data["_outdoor_temperature"]),
        'target_temperature': convert_to_f(data["_target_temperature"])
    }

    print(f'Midea: {midea_data}')

    return midea_data
