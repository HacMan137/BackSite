import json

CONFIG_PATH = "/opt/configuration/config.json"

def get_configuration():
    with open(CONFIG_PATH,"r") as f:
        data = json.loads(f.read())
        return data