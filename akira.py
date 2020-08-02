import os, asyncio
from telegram.ext import Updater
from telethon.sessions import MemorySession
from telethon.tl.types import DocumentAttributeAudio
from telethon import TelegramClient, events

akira = "0.1"

def log(text): print(f"[Akira] {text}")

class Akira(TelegramClient):
	async def connect(self):
		await super().connect()
		await self.catch_up()

client = Akira(MemorySession(), os.environ.get("API_ID"), os.environ.get("API_HASH")).start(bot_token=os.environ.get("BOT_TOKEN"))

@client.on(events.NewMessage(pattern="/start"))
async def akira_start(event):
	print(event)
	await event.reply("Hi! Im Akira.")

async def main():
	log(f"Starting Akira {akira}...")

	# Dummy webhook
	updater = Updater(os.environ.get("BOT_TOKEN"), use_context=True)
	updater.start_webhook(listen="0.0.0.0", port=os.environ.get("PORT"), url_path=os.environ.get("BOT_TOKEN"))
	updater.bot.set_webhook(os.environ.get("URL") + "/" + os.environ.get("BOT_TOKEN"))

	log("Started.")
	await client.run_until_disconnected()

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
