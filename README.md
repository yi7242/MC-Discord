# MC-Discord
## 概要
マイクラとDiscordの連携機能が充実したDiscordボットです

主な機能として
- サーバープロセスの起動・停止
- Discordからマイクラへのチャット・コマンドの送信
- サーバーログをDiscordへ送信

等があります。

## 使い方
(今度書き直します)

Discord Developerへアクセス、APIキー発行、.envに貼っておく

その他serveridやらチャットidやらs3のキーやらを.envに貼っておく

`sudo apt update`

`sudo apt install python3`

server.jarがあるディレクトリで以下を実行

`git clone https://github.com/yi7242/MC-Discord.git`

`python3 -m pip install -r MC-Discord/requirements.txt`

`python3 MC-Discord/bot.py`
