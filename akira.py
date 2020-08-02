import os, asyncio
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from telethon.sessions import MemorySession
from telethon.tl.types import DocumentAttributeAudio
from telethon import TelegramClient, events

akira = "0.1"

def log(text): print(f"[Akira] {text}")

client = TelegramClient(MemorySession(), os.environ.get("API_ID"), os.environ.get("API_HASH")).start(bot_token=os.environ.get("BOT_TOKEN"))

@client.on(events.NewMessage(pattern="/start"))
async def akira_start(event):
	print(event)
	await event.reply("Hi! Im Akira.")

async def main():
	log(f"Starting Akira {akira}...")
	log("Creating bot client...")
	bot = Bot(token=os.environ.get("BOT_TOKEN"))
	dp = Dispatcher(bot)

	async def on_startup(dp): await bot.set_webhook(os.environ.get("URL") + "/" + os.environ.get("BOT_TOKEN"))
	async def on_shutdown(dp): await bot.delete_webhook()

	log("Started.")
	#await client.catch_up()
	start_webhook(
		dispatcher=dp,
		webhook_path="/" + os.environ.get("BOT_TOKEN"),
		on_startup=on_startup,
		on_shutdown=on_shutdown,
		port=os.environ.get("PORT")
	)

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
