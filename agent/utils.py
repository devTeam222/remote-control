import json
import uuid

def get_mac():
    mac = uuid.getnode()
    return ':'.join(f'{(mac >> ele) & 0xff:02x}' for ele in range(40, -1, -8))

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)