import os, tempfile, shutil, aiohttp
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telethon.sessions import MemorySession
from telethon.utils import get_message_id
from telethon import TelegramClient

akira = "0.1"

def log(text): print(f"[Akira] {text}")

client = TelegramClient(MemorySession(), os.environ.get("API_ID"), os.environ.get("API_HASH")).start(bot_token=os.environ.get("BOT_TOKEN"))
bot = Bot(token=os.environ.get("BOT_TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=["start"], run_task=True)
async def akira_start(message: types.Message):
	await message.reply("Hi! Im Akira.")

@dp.message_handler(commands=["ipfs"], run_task=True)
async def akira_ipfs(message: types.Message):
	temp_dir = tempfile.mkdtemp(dir=tempfile.gettempdir())
	chat = await client.get_entity(message.chat.id)
	telethon_message = await client.get_messages(chat, ids=message.message_id)
	if telethon_message.reply_to_msg_id:
		telethon_reply_message = await client.get_messages(chat, ids=telethon_message.reply_to_msg_id)
		if "photo" in telethon_reply_message.media:
			print("Photo detected")
		elif "document" in telethon_reply_message.media:
			print("Document detected")
		else:
			print("No file detected")
		reply = await message.reply("Downloading...")
		try:
			downloaded_file = await telethon_reply_message.download_media(temp_dir)
		except:
			await reply.delete()
			await message.reply("An error occurred while downloading a file.")
			return
		await reply.edit_text("Uploading...")
		try:
			async with aiohttp.ClientSession() as session:
				response = await session.post("https://ipfsupload.herokuapp.com/upload", data={"file": open(downloaded_file, "rb")})
		except:
			await reply.delete()
			await message.reply("An error occurred while uploading a file.")
			return
		await reply.delete()
		await message.reply(await response.text())
	else:
		await message.reply("Please respond to a message with a file.")
	shutil.rmtree(temp_dir)

@dp.message_handler(commands=["yt2a"], run_task=True)
async def akira_ipfs(message: types.Message):
	await message.reply("This command is not available now.")

@dp.message_handler(commands=["weather"], run_task=True)
async def akira_ipfs(message: types.Message):
	await message.reply("This command is not available now.")

@dp.message_handler(commands=["qr"], run_task=True)
async def akira_ipfs(message: types.Message):
	await message.reply("This command is not available now.")

if __name__ == "__main__":
	log(f"Starting Akira {akira}...")

	async def on_startup(dp): await bot.set_webhook(os.environ.get("URL") + "/" + os.environ.get("BOT_TOKEN"))
	async def on_shutdown(dp): await bot.delete_webhook()

	log("Started.")
	start_webhook(
		dispatcher=dp,
		webhook_path="/" + os.environ.get("BOT_TOKEN"),
		on_startup=on_startup,
		on_shutdown=on_shutdown,
		port=os.environ.get("PORT")
	)
