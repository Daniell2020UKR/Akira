import os, importlib.util, builtins, pymongo
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telethon.sessions import MemorySession
from telethon.tl.types import DocumentAttributeAudio
from telethon.utils import resolve_bot_file_id
from telethon import TelegramClient

akira = "0.1"

def log(text): print(f"[Akira] {text}")

def load_module(path):
	spec = importlib.util.spec_from_file_location(path.split("/")[-1].split(".")[0], path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	module.register()

def db_insert(db, name, data):
	if db_find(db, name): raise Exception("Key is already in database.")
	else: db.insert_one({"name": name, "value": data})

def db_update(db, name, data):
	if not db_find(db, name): raise Exception("Key is not in database.")
	else: db.update_one({"name": name}, {"$set": {"name": name, "value": data}})

def db_delete(db, name):
	if not db_find(db, name): raise Exception("Key is not in database.")
	else: db.delete_one({"name": name})

def db_find(db, name):
	return db.find_one({"name": name})

builtins.db_insert = db_insert
builtins.db_update = db_update
builtins.db_delete = db_delete
builtins.db_find = db_find

if __name__ == "__main__":
	log(f"Starting Akira {akira}...")
	log("Creating bot client...")
	builtins.client = TelegramClient(MemorySession(), os.environ.get("API_ID"), os.environ.get("API_HASH")).start(bot_token=os.environ.get("BOT_TOKEN"))
	builtins.bot = Bot(token=os.environ.get("BOT_TOKEN"))
	builtins.dp = Dispatcher(bot, storage=MemoryStorage())

	log("Connecting to MongoDB...")
	mdb_server = pymongo.MongoClient(os.environ.get("MDB_HOST"))["akira"]
	builtins.user_data = mdb_server["user"]
	builtins.chat_data = mdb_server["chat"]
	builtins.bot_data = mdb_server["bot"]

	for module in os.listdir("modules"):
		if module != "__pycache__": load_module(f"modules/{module}")

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
