#!/bin/bash

read -sp "Enter your Discord Bot Token: " TOKEN
echo
read -p "Enter your Discord Channel ID: " CHANNEL_ID

export DISCORD_TOKEN=$TOKEN
export DISCORD_CHANNEL_ID=$CHANNEL_ID

echo "Starting bot..."

curl -s https://raw.githubusercontent.com/UniversPlayer/discord-bot-temp-mail/refs/heads/main/main.py -o main.py

python3 main.py
