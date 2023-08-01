# Discordサーバーのサーバーid、スラッシュコマンドのsyncのために使用
SERVER_ID = 1111111111111111111

# ログを送信するチャンネルのid
LOG_CHANNEL_ID = 2222222222222222222

# マイクラサーバーのipアドレス
IPADDRESS = "111.222.333.444"

# DiscordボットのAPI KEY
APIKEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# サーバーの起動コマンドをスペース区切りで配列に入力
# バニラの場合は以下の様になる
# BOOT_COMMAND = ["java", "-Xmx1024M", "-Xms1024M", "-jar", "minecraft_server.1.20.1.jar", "nogui"]
# 以下はFTB University 1.16の場合
BOOT_COMMAND = ["jre/jdk8u312-b07-jre/bin/java", "-javaagent:log4jfix/Log4jPatcher-1.0.0.jar", "-XX:+UseG1GC", "-XX:+UnlockExperimentalVMOptions", "-Xmx6144M", "-Xms4096M", "-jar", "forge-1.16.5-36.2.35.jar", "nogui"]
