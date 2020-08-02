import os
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telethon.functions.channels import GetMessagesRequest
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
	print(message)
	result = client(GetMessagesRequest(
		channel=message.chat.username,
		id=[message.message_id]
	))
	print(result)
	
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
