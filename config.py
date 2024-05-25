from os.path import join, dirname
from dotenv import dotenv_values

config = {}

# .envが存在する場合、.envでconfigを上書き
config.update(dotenv_values(join(dirname(__file__), ".env")))

SERVER_ID = config["SERVER_ID"]
SEND_CHAT = True if config["SEND_CHAT"] == "true" else False
SEND_LOG = True if config["SEND_LOG"] == "true" else False
LOG_CHANNEL_ID = int(config["LOG_CHANNEL_ID"])
CHAT_CHANNEL_ID = int(config["CHAT_CHANNEL_ID"])
IPADDRESS = config["IPADDRESS"]
APIKEY = config["APIKEY"]
BOOT_COMMAND = list(config["BOOT_COMMAND"].split())
LOG_INTERVAL = float(config["LOG_INTERVAL"])
CHAT_DETECT_STR = config["CHAT_DETECT_STR"]
S3_URL = config["S3-URL"]
AWS_ACCESS_KEY_ID = config["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = config["AWS_SECRET_ACCESS_KEY"]
BUCKET_NAME = config["BUCKET_NAME"]
