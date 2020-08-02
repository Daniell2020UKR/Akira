import os, tempfile, shutil, requests
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
		reply = await message.reply("Downloading...")
		dfile = await telethon_reply_message.download_media(temp_dir)
		reply.edit("Uploading...")
		res = requests.post("https://ipfsupload.herokuapp.com/upload", files={"file": open(dfile, "rb")})
		reply.delete()
		await message.reply(res.text)
	else:
		await message.reply("Please respond to a message with a file.")
	shutil.rmtree(temp_dir)

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
