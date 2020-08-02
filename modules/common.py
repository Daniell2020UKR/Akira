from aiogram import types

async def akira_start(message: types.Message):
	print(message)
	await message.reply('Test')

def register():
	dp.register_message_handler(akira_start, commands=['start'], run_task=True)
