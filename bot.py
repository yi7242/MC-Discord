import discord
from discord.ext import tasks
from discord import app_commands
import sys
import subprocess
from threading import Thread
from queue import Queue, Empty
from sys import exit

# configファイル
import config

ON_POSIX = 'posix' in sys.builtin_module_names
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
server_online = False
proc = None

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        if line == "":
            continue
        else:
            print(line, end="")
            queue.put(line)
    out.close()


# log_channel = None
# chat_channel = None


@client.event
async def on_ready():
    global log_channel, chat_channel
    print(f'Logged in as: {client.user.name}')
    print(f'With ID: {client.user.id}')
    log_channel = client.get_channel(config.LOG_CHANNEL_ID)
    chat_channel = client.get_channel(config.CHAT_CHANNEL_ID)
    online_check.start()
    log_output.start()
    await tree.sync(guild=discord.Object(id=config.SERVER_ID))

@client.event
async def on_message(message):
    if message.author.bot:
        return
    global server_online, proc
    if server_online and message.channel == chat_channel:
        command = f'tellraw @a \"<{message.author.global_name}> {message.content}\"\n'
        proc.stdin.write(command)
        proc.stdin.flush()

@tree.command(guild=discord.Object(id=config.SERVER_ID), description="ヘルプを表示")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message("""    
    --ヘルプ--
    `/help` ヘルプを表示
    `/ipaddress` ipアドレスを表示
    --サーバー起動--
    `/status` サーバーのオンライン状態を表示
    `/start` サーバーの起動
    `/stop` サーバーの停止
    --マイクラ--
    `/say メッセージ` サーバーチャットにメッセージを送信
    `/list` 現在オンラインのプレイヤー数を表示
    `/exe コマンド` マイクラ内でコマンドを実行、管理者権限が必要です
    --ボット--
    `/kill` botを強制終了、管理者権限が必要です""")

@tree.command(guild=discord.Object(id=config.SERVER_ID), description="ipアドレスを表示")
async def ipaddress(interaction: discord.Interaction):
    await interaction.response.send_message(f"ipアドレスは{config.IPADDRESS}です。")


@tree.command(guild=discord.Object(id=config.SERVER_ID), description="サーバーを起動します")
async def start(interaction: discord.Interaction):
    global server_online, proc, log_queue, output_thread
    if server_online == False:
        proc = subprocess.Popen(config.BOOT_COMMAND,  stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding="utf-8", bufsize=1, close_fds=ON_POSIX)
        server_online = True
        log_queue = Queue()
        output_thread = Thread(target=enqueue_output, args=(proc.stdout, log_queue))
        output_thread.daemon = True
        output_thread.start()
        await interaction.response.send_message("起動命令を送信しました")
    else:
        await interaction.response.send_message("サーバーは既にオンラインです")


@tree.command(guild=discord.Object(id=config.SERVER_ID), description="サーバーを停止します")
async def stop(interaction: discord.Interaction):
    global server_online, proc
    if server_online:
        proc.stdin.write("stop\n")
        proc.stdin.flush()
        log_queue = None
        await interaction.response.send_message("停止命令を送信しました")
    else:
        await interaction.response.send_message("サーバーは既にオフラインです")


@tree.command(guild=discord.Object(id=config.SERVER_ID), description="マイクラ内のチャットにメッセージを送信します")
async def say(interaction: discord.Interaction, message: str):
    global server_online, proc
    if server_online:
        proc.stdin.write("say "+message + "\n")
        proc.stdin.flush()
        await interaction.response.send_message("発言を送信しました")
    else:
        print(message.encode('shift_jis'))
        await interaction.response.send_message("サーバーはオフラインです")


@tree.command(guild=discord.Object(id=config.SERVER_ID), description="指定したコマンドを送信します")
@app_commands.default_permissions(administrator=True)
async def exe(interaction: discord.Interaction, message: str):
    global server_online, proc
    if server_online:
        proc.stdin.write(message + "\n")
        proc.stdin.flush()
        await interaction.response.send_message("コマンドを送信しました")
    else:
        await interaction.response.send_message("サーバーはオフラインです")


@tree.command(guild=discord.Object(id=config.SERVER_ID), description="現在のサーバーの接続人数を確認します")
async def list(interaction: discord.Interaction):
    global server_online, proc
    if not server_online:
        await interaction.response.send_message("サーバーはオフラインです")
    else:
        proc.stdin.write("list\n")
        proc.stdin.flush()
        await interaction.response.send_message("listコマンドを送信しました")


@tree.command(guild=discord.Object(id=config.SERVER_ID), description="サーバーのオンライン状態を確認します")
async def status(interaction: discord.Interaction):
    global server_online
    if server_online:
        await interaction.response.send_message("サーバーはオンラインです")
    else:
        await interaction.response.send_message("サーバーはオフラインです")


@tree.command(guild=discord.Object(id=config.SERVER_ID), description="botを停止します。管理者権限が必要です。")
@app_commands.default_permissions(administrator=True)
async def kill(interaction: discord.Interaction):
    print("killed")
    if server_online:
        proc.stdin.write("stop\n")
        proc.stdin.flush()
        await interaction.response.send_message("botを停止します")
    exit()


# Background tasks
@tasks.loop(seconds=0.5)
async def online_check():
    await client.wait_until_ready()
    global server_online, proc
    if proc != None:
        if proc.poll() == None:
            server_online = True
        else:
            server_online = False


@tasks.loop(seconds=config.LOG_INTERVAL)
async def log_output():
    await client.wait_until_ready()
    global server_online, proc
    if server_online:
        log = ""
        chat_log = ""
        while True:
            try:
                log_line = log_queue.get_nowait()
                if "[minecraft/DedicatedServer]" in log_line:
                    chat_log += log_line
                log += log_line
            except Empty:
                break
        await check_send(chat_log, chat_channel)
        await check_send(log, log_channel)

# 文字数をチェックし、送信する
async def check_send(log, channel):
    if log != "":
        if len(log) > 2000:
            await channel.send(log[:1900] + "... 文字数が2000文字を超えるため省略")
        else:
            await channel.send(log)

async def online_check_loop():
    await online_check.start()
async def log_output_loop():
    await log_output.start()

client.run(config.APIKEY)