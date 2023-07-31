# Discordサーバーのサーバーid、スラッシュコマンドのsyncのために使用
serverid = 1111111111111111111

# ログを送信するチャンネルのid
log_channel_id = 2222222222222222222

# マイクラサーバーのipアドレス
ip = "111.222.333.444"

# DiscordボットのAPI KEY
APIKEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# サーバーの起動コマンドをスペース区切りで配列に入力
# バニラの場合は以下の様になる
# boot_command = ["java", "-Xmx1024M", "-Xms1024M", "-jar", "minecraft_server.1.20.1.jar", "nogui"]
# 以下はFTB University 1.16の場合
boot_command = ["jre/jdk8u312-b07-jre/bin/java", "-javaagent:log4jfix/Log4jPatcher-1.0.0.jar", "-XX:+UseG1GC", "-XX:+UnlockExperimentalVMOptions", "-Xmx6144M", "-Xms4096M", "-jar", "forge-1.16.5-36.2.35.jar", "nogui"]
