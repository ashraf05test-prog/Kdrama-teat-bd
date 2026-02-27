import asyncio
from pyrogram import Client
import os

async def upload_to_telegram(file_path, title, caption):
    bot_token = os.environ['TG_BOT_TOKEN']
    channel_id = int(os.environ['TG_CHANNEL_ID'])

    async with Client("uploader_bot", bot_token=bot_token) as app:
        msg = await app.send_video(
            chat_id=channel_id,
            video=file_path,
            caption=f"**{title}**\n\n{caption}",
            supports_streaming=True,
            progress=None  # You can add progress if wanted
        )
        return f"https://t.me/{os.environ['TG_CHANNEL_USERNAME'].lstrip('@')}/{msg.id}"