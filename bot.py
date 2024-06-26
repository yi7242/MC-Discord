from os import name as osname
import zipfile
import shutil
import time
import datetime
import discord
from discord.ext import tasks
from discord import app_commands
import boto3
import sys
import subprocess
from threading import Thread
from queue import Queue, Empty
from sys import exit

# configファイル
import config
import aws


windows = False
if osname == "nt":
    windows = True
ON_POSIX = "posix" in sys.builtin_module_names
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
proc = None
log_queue = Queue()
divided_chat_queue = Queue()
divided_log_queue = Queue()


def enqueue_output(out, queue):
    while True:
        line = out.readline()
        if line == b"":
            continue
        else:
            if windows:
                decode_line = line.decode("cp932")
            else:
                decode_line = line.decode("utf-8")
            print(decode_line, end="")
            queue.put(decode_line)


@client.event
async def on_ready():
    global log_channel, chat_channel
    print(f"Logged in as: {client.user.name}")
    print(f"With ID: {client.user.id}")
    log_channel = client.get_channel(config.LOG_CHANNEL_ID)
    chat_channel = client.get_channel(config.CHAT_CHANNEL_ID)
    log_output.start()
    await tree.sync(guild=discord.Object(id=config.SERVER_ID))


@client.event
async def on_message(message):
    if message.author.bot:
        return
    global proc
    if online_check() and message.channel == chat_channel:
        command = f'tellraw @a "<{message.author.global_name}> {message.content}"'
        send_command(command)


@tree.command(guild=discord.Object(id=config.SERVER_ID), description="ヘルプを表示")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(
        """    
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
    `/exe コマンド` マイクラ内でコマンドを実行、管理者権限が必要
    
    ※以下は必要な場合のみ使用してください
    `/termmc` サーバーにSIGTERMシグナルを送信
    `/killmc` xX最終奥義Xx サーバープロセスをkill
    `/killbot` botを強制終了、管理者権限が必要です"""
    )


@tree.command(guild=discord.Object(id=config.SERVER_ID), description="ipアドレスを表示")
async def ipaddress(interaction: discord.Interaction):
    await interaction.response.send_message(f"ipアドレスは{config.IPADDRESS}です。")


@tree.command(
    guild=discord.Object(id=config.SERVER_ID), description="サーバーを起動します"
)
async def start(interaction: discord.Interaction):
    global proc, log_queue, output_thread
    if not online_check():
        proc = subprocess.Popen(
            config.BOOT_COMMAND,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            close_fds=ON_POSIX,
        )
        output_thread = Thread(target=enqueue_output, args=(proc.stdout, log_queue))
        output_thread.daemon = True
        output_thread.start()
        await interaction.response.send_message("起動命令を送信しました")
    else:
        await interaction.response.send_message("サーバーは既にオンラインです")


@tree.command(
    guild=discord.Object(id=config.SERVER_ID), description="サーバーを停止します"
)
async def stop(interaction: discord.Interaction):
    global proc, log_queue
    if online_check():
        send_command("stop")
        await interaction.response.send_message("停止命令を送信しました")
    else:
        await interaction.response.send_message("サーバーは既にオフラインです")


@tree.command(
    guild=discord.Object(id=config.SERVER_ID),
    description="マイクラ内のチャットにメッセージを送信します",
)
async def say(interaction: discord.Interaction, message: str):
    global proc
    if online_check():
        send_command("say " + message)
        await interaction.response.send_message("発言を送信しました")
    else:
        await interaction.response.send_message("サーバーはオフラインです")


@tree.command(
    guild=discord.Object(id=config.SERVER_ID),
    description="指定したコマンドを送信します",
)
@app_commands.default_permissions(administrator=True)
async def exe(interaction: discord.Interaction, message: str):
    global proc
    if online_check():
        send_command(message)
        await interaction.response.send_message("コマンドを送信しました")
    else:
        await interaction.response.send_message("サーバーはオフラインです")


@tree.command(
    guild=discord.Object(id=config.SERVER_ID),
    description="現在のサーバーの接続人数を確認します",
)
async def list(interaction: discord.Interaction):
    global proc
    if not online_check():
        await interaction.response.send_message("サーバーはオフラインです")
    else:
        send_command("list")
        await interaction.response.send_message("listコマンドを送信しました")


@tree.command(
    guild=discord.Object(id=config.SERVER_ID),
    description="サーバーのオンライン状態を確認します",
)
async def status(interaction: discord.Interaction):
    if online_check():
        await interaction.response.send_message("サーバーはオンラインです")
    else:
        await interaction.response.send_message("サーバーはオフラインです")


@tree.command(
    guild=discord.Object(id=config.SERVER_ID),
    description="botを停止します。管理者権限が必要です。",
)
@app_commands.default_permissions(administrator=True)
async def killbot(interaction: discord.Interaction):
    print("killed")
    if online_check():
        send_command("stop")
        await interaction.response.send_message("botを停止します")
    exit()


@tree.command(
    guild=discord.Object(id=config.SERVER_ID),
    description="サーバーにSIGTERMを送信します。",
)
async def termmc(interaction: discord.Interaction):
    if online_check():
        proc.terminate()
        await interaction.response.send_message("botにSIGTERMを送信しました")
    else:
        await interaction.response.send_message("サーバーはオフラインです")


@tree.command(
    guild=discord.Object(id=config.SERVER_ID), description="サーバーをkillします。"
)
async def killmc(interaction: discord.Interaction):
    if online_check():
        proc.kill()
        await interaction.response.send_message("サーバーをkillしました。")
    else:
        await interaction.response.send_message("サーバーはオフラインです")


@tree.command(
    guild=discord.Object(id=config.SERVER_ID),
    description="ワールドのバックアップを作成します。",
)
async def backup(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    s3_client: boto3.client = boto3.client(
        service_name="s3",
        endpoint_url=config.S3_URL,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name="auto",
    )

    # バケット内の全オブジェクトをリスト
    response = s3_client.list_objects(Bucket=config.BUCKET_NAME)
    if len(response["Contents"]) >= 5:
        # 最古のファイルを特定する
        oldest_file = None
        oldest_file_date = None

        for obj in response["Contents"]:
            file_key = obj["Key"]
            last_modified = obj["LastModified"]
            if oldest_file_date is None:
                oldest_file_date = last_modified
                oldest_file = file_key
            else:
                if last_modified < oldest_file_date:
                    oldest_file_date = last_modified
                    oldest_file = file_key

        # 最古のファイルを削除する
        if oldest_file:
            s3_client.delete_object(Bucket=config.BUCKET_NAME, Key=oldest_file)
            print(
                f"Deleted oldest file: {oldest_file} (Last Modified: {oldest_file_date})"
            )
        else:
            print("No files found to delete.")
    filename = "world_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    shutil.make_archive(filename, format="zip", root_dir="world")
    url = aws.upload_and_get_url(s3_client, config.BUCKET_NAME, filename + ".zip")
    await interaction.followup.send(f"バックアップが作成されました: {url}")


@tasks.loop(seconds=config.LOG_INTERVAL)
async def log_output():
    await client.wait_until_ready()
    global proc
    if online_check():
        log = ""
        chat_log = ""
        while True:
            try:
                log_line = log_queue.get_nowait()
                if config.CHAT_DETECT_STR in log_line:
                    detectind = log_line.find(config.CHAT_DETECT_STR)
                    # スペース分1足してる
                    chat_log += log_line[len(config.CHAT_DETECT_STR) + detectind + 1 :]
                log += log_line
            except Empty:
                break
        if log != "":
            for i in range(0, len(log), 2000):
                divided_log_queue.put(log[i : i + 2000])
        if chat_log != "":
            for i in range(0, len(chat_log), 2000):
                divided_chat_queue.put(chat_log[i : i + 2000])
        if config.SEND_CHAT:
            await message_sender(divided_chat_queue, chat_channel)
        if config.SEND_LOG:
            await message_sender(divided_log_queue, log_channel)


# 文字数をチェックし、送信する
async def message_sender(divided_queue, channel):
    if not divided_queue.empty():
        await channel.send(divided_queue.get())


def online_check():
    global proc
    if proc is not None:
        if proc.poll() is None:
            return True
        else:
            return False


def send_command(command, raw=False):
    global proc
    if online_check():
        if not raw:
            command += "\n"
        proc.stdin.write(command.encode("utf-8"))
        proc.stdin.flush()


async def log_output_loop():
    await log_output.start()


client.run(config.APIKEY)
