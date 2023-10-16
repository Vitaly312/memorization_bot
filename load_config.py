import os
import configparser
from dotenv import load_dotenv


config = configparser.ConfigParser()
load_dotenv()
load_dotenv('.env.example')

config_path = os.environ.get("MEMORYBOT_CONFIG_PATH", 'config.example.ini')
try:
    with open(config_path) as file:
        config.read_file(file)
except FileNotFoundError:
    msg = 'PATH to config file not exists. Please, set\
 environment variable MEMORYBOT_CONFIG_PATH to actual path to config.ini file\
 or delete this variable to use default config.'
    raise FileNotFoundError(msg)
