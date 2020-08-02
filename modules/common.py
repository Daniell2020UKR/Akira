from aiogram import types
from telethon.utils import resolve_bot_file_id

async def akira_start(message: types.Message):
	await message.reply("Hi! Im Akira.")

async def akira_yt2a(message: types.Message):
	await message.reply("This command is not available now.")

async def akira_ipfs(message: types.Message):
	if message.reply_to_message:
		print(message)
		if message.reply_to_message.document:
			resolved_id = resolve_bot_file_id(message.reply_to_message.document.file_id)
			print(resolved_id)
			await message.reply("This command is not available now.")
		else:
			await message.reply("Please respond to a message with a file.")
	else:
		await message.reply("Please respond to a message with a file.")

def register():
	dp.register_message_handler(akira_start, commands=["start"], run_task=True)
	dp.register_message_handler(akira_yt2a, commands=["yt2a"], run_task=True)
	dp.register_message_handler(akira_ipfs, commands=["ipfs"], run_task=True)
