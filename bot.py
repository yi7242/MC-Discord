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
log_queue, output_thread = None, None


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        if line == "":
            continue
        else:
            print(line)
            queue.put(line)
    out.close()

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
server_online = False
proc = None
log_channel = None


@client.event
async def on_ready():
    global log_channel
    print(f'Logged in as: {client.user.name}')
    print(f'With ID: {client.user.id}')
    log_channel = client.get_channel(config.log_channel_id)
    online_check.start()
    log_output.start()
    await tree.sync(guild=discord.Object(id=config.serverid))



@tree.command(guild=discord.Object(id=config.serverid), description="ヘルプを表示")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message("""    
    --ヘルプ--
    `/help` ヘルプを表示
    `/ip` ipアドレスを表示
    --サーバー起動--
    `/status` サーバーのオンライン状態を表示
    `/start` サーバーの起動
    `/stop` サーバーの停止
    --マイクラ--
    `/say メッセージ` サーバーチャットにメッセージを送信
    `/list` 現在オンラインのプレイヤー数を表示
    `/exe コマンド` マイクラ内でコマンドを実行
    --ボット--
    `/kill` botを強制終了、管理者権限が必要です""")

@tree.command(guild=discord.Object(id=config.serverid), description="ipアドレスを表示")
async def ip(interaction: discord.Interaction):
    await interaction.response.send_message(f"ipアドレスは{config.ip}です。")


@tree.command(guild=discord.Object(id=config.serverid), description="サーバーを起動します")
async def start(interaction: discord.Interaction):
    print("hello")
    global server_online, proc, log_queue, output_thread
    if server_online == False:
        proc = subprocess.Popen(config.boot_command,  stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding="utf-8", bufsize=1, close_fds=ON_POSIX)
        server_online = True
        log_queue = Queue()
        output_thread = Thread(target=enqueue_output, args=(proc.stdout, log_queue))
        output_thread.daemon = True
        output_thread.start()
        print("open")
        await interaction.response.send_message("起動命令を送信しました")
    else:
        await interaction.response.send_message("サーバーは既にオンラインです")
        print("nono")


@tree.command(guild=discord.Object(id=config.serverid), description="サーバーを停止します")
async def stop(interaction: discord.Interaction):
    print("stop")
    global server_online, proc
    if server_online:
        proc.stdin.write("stop\n")
        proc.stdin.flush()
        log_queue = None
        await interaction.response.send_message("停止命令を送信しました")
    else:
        await interaction.response.send_message("サーバーは既にオフラインです")


@tree.command(guild=discord.Object(id=config.serverid), description="マイクラ内のチャットにメッセージを送信します")
async def say(interaction: discord.Interaction, message: str):
    global server_online, proc
    if server_online:
        proc.stdin.write("say "+message + "\n")
        proc.stdin.flush()
        await interaction.response.send_message("発言を送信しました")
    else:
        type(message)
        print(message.encode('shift_jis'))
        await interaction.response.send_message("サーバーはオフラインです")


@tree.command(guild=discord.Object(id=config.serverid), description="指定したコマンドを送信します")
@app_commands.default_permissions(administrator=True)
async def exe(interaction: discord.Interaction, message: str):
    global server_online, proc
    print("command is", message)
    if server_online:
        proc.stdin.write(message + "\n")
        proc.stdin.flush()
        await interaction.response.send_message("コマンドを送信しました")
    else:
        await interaction.response.send_message("サーバーはオフラインです")


@tree.command(guild=discord.Object(id=config.serverid), description="現在のサーバーの接続人数を確認します")
async def list(interaction: discord.Interaction):
    global server_online, proc
    if not server_online:
        await interaction.response.send_message("サーバーはオフラインです")
    else:
        proc.stdin.write("list\n")
        proc.stdin.flush()
        await interaction.response.send_message("listコマンドを送信しました")


@tree.command(guild=discord.Object(id=config.serverid), description="サーバーのオンライン状態を確認します")
async def status(interaction: discord.Interaction):
    global server_online
    if server_online:
        await interaction.response.send_message("サーバーはオンラインです")
    else:
        await interaction.response.send_message("サーバーはオフラインです")


@tree.command(guild=discord.Object(id=config.serverid), description="botを停止します。管理者権限が必要です。")
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


@tasks.loop(seconds=0.5)
async def log_output():
    await client.wait_until_ready()
    global server_online, proc
    if server_online:
        log = ""
        while True:
            try:
                log += log_queue.get_nowait()
            except Empty:
                break
        if log != "":
            await log_channel.send(log)

async def online_check_loop():
    await online_check.start()
async def log_output_loop():
    await log_output.start()

client.run(config.APIKEY)


