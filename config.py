# config.py

import json

def load_config(file_path='C:/Users/Administrator/Desktop/Fuel Scraping/config.json'):
    """
    Load configuration settings from a JSON file.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

config = load_config()

def get(key):
    """
    Get a configuration value for the given key.
    """
    return config.get(key)
