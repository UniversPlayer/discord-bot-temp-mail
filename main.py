import discord
import secrets
import string
import os
import asyncio
import json
import aiohttp

TOKEN = input("Enter your Discord Bot Token: ")
CHANNEL_ID = int(input("Enter the Channel ID to allow commands in: "))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.dm_messages = True

client = discord.Client(intents=intents)

token_map = {}

MAILTM_API = "https://api.mail.tm"

async def create_mail_account():
    async with aiohttp.ClientSession() as session:
        # Get domain
        async with session.get(f"{MAILTM_API}/domains") as r:
            data = await r.json()
            domain = data["hydra:member"][0]["domain"]

        username = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10))
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        email = f"{username}@{domain}"

        # Create account
        await session.post(f"{MAILTM_API}/accounts", json={"address": email, "password": password})
        # Get token
        async with session.post(f"{MAILTM_API}/token", json={"address": email, "password": password}) as r:
            token_data = await r.json()
            token = token_data["token"]

        return email, password, token

async def fetch_inbox(token):
    async with aiohttp.ClientSession(headers={"Authorization": f"Bearer {token}"}) as session:
        async with session.get(f"{MAILTM_API}/messages") as r:
            return await r.json()

@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != CHANNEL_ID:
        return

    content = message.content.strip().split()
    cmd = content[0].lower()

    if cmd == "$mail":
        await message.channel.send("Generating Mail...")
        email, password, api_token = await create_mail_account()

        user_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(7))
        token_map[user_token] = {
            "email": email,
            "password": password,
            "api_token": api_token
        }

        await message.channel.send(f"Mail generated. Sending mail to {message.author.mention}")
        dm = await message.author.create_dm()
        await dm.send(f"📩 **Your Temp Mail:** `{email}`\n🔐 **Your Token:** `{user_token}`\nUse `$inbox {user_token}` to check inbox.")

    elif cmd == "$inbox" and len(content) == 2:
        user_token = content[1]
        if user_token not in token_map:
            await message.channel.send("❌ Invalid or expired token.")
            return

        inbox_data = await fetch_inbox(token_map[user_token]["api_token"])
        messages = inbox_data.get("hydra:member", [])

        if not messages:
            await message.channel.send("📭 Inbox is empty.")
        else:
            reply = f"📬 **Inbox for token `{user_token}`:**\n"
            for m in messages[:5]:
                sender = m['from']['address']
                subject = m['subject']
                reply += f"\n- **From:** `{sender}` | **Subject:** `{subject}`"
            await message.channel.send(reply)

client.run(TOKEN)
