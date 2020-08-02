from aiogram import types
from telethon.utils import resolve_bot_file_id

async def akira_start(message: types.Message):
	
	await message.reply("Hi! Im Akira.")

async def akira_yt2a(message: types.Message):
	await message.reply("This command is not available now.")

async def akira_ipfs(message: types.Message):
	print(message)
	await message.reply("This command is not available now.")
	print(message.text)
	print(message["text"])

def register():
	dp.register_message_handler(akira_start, commands=["start"], run_task=True)
	dp.register_message_handler(akira_yt2a, commands=["yt2a"], run_task=True)
	dp.register_message_handler(akira_ipfs, commands=["ipfs"], run_task=True)
