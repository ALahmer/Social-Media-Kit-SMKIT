import json
import logging


env_file = 'env.json'


def load_from_env():
    try:
        with open(env_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Environment file not found.")
        return None
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from the environment file.")
        return None


def save_to_env(data):
    try:
        with open(env_file, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        logging.error(f"Error saving to env file: {e}")
