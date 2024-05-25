from os.path import join, dirname
from dotenv import dotenv_values

# 自分で設定する項目
# ディレクトリ内に.envファイルが存在する場合、.envの設定が優先されます
config = {
    # Discordサーバーのサーバーid、スラッシュコマンドのsyncのために使用
    "SERVER_ID": "1111111111111111111",
    # チャットとログの送信の有無 true/false
    "SEND_CHAT": "true",
    "SEND_LOG": "true",
    # ログを送信するチャンネルのid
    "LOG_CHANNEL_ID": "1111111111111111111",
    # チャットを送信するチャンネルのid
    "CHAT_CHANNEL_ID": "1111111111111111111",
    # マイクラサーバーのipアドレス
    "IPADDRESS": "111.222.333.444",
    # DiscordボットのAPI KEY
    "APIKEY": "YOUR_DISCORD_API_KEY",
    # サーバーの起動コマンドをスペース区切りで配列に入力
    # バニラの場合は以下の様になる
    "BOOT_COMMAND": "java -Xmx4G -Xms4G -jar server.jar nogui",
    # 以下はFTB University 1.16の場合
    # "BOOT_COMMAND" : "jre/jdk8u312-b07-jre/bin/java -javaagent:log4jfix/Log4jPatcher-1.0.0.jar -XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -Xmx6144M -Xms4096M -jar forge-1.16.5-36.2.35.jar nogui",
    # ログの送信間隔(秒)
    "LOG_INTERVAL": "0.5",
    # チャットメッセージの検知に使用する文字列
    # バニラの場合は以下のようになる
    "CHAT_DETECT_STR": "[Server thread/INFO]:",
    # 以下はFTB University 1.16の場合
    # "CHAT_DETECT_STR" : "[minecraft/DedicatedServer]:"
    # S3用URL
    "S3-URL": "",
}

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
