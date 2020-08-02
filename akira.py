import os, asyncio
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

	# Dummy webhook
	await bot.set_webhook(os.environ.get("URL") + "/" + os.environ.get("BOT_TOKEN"))
	async def webhook(request): return web.Response(text="ACK")
	app = web.Application()
	app.router.add_post("/" + os.environ.get("BOT_TOKEN"), webhook)
	web.run_app(app, port=os.environ.get("PORT"))

	log("Started.")
	#await client.catch_up()

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
