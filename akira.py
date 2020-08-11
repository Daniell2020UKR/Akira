import os, tempfile, shutil, aiohttp, aiofiles, urllib
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto, DocumentAttributeVideo
from telethon.sessions import MemorySession
from telethon.utils import get_message_id
from telethon import TelegramClient

akira = "0.1"
akira_dir = os.getcwd() + "/akira"

def log(text): print(f"[Akira] {text}")

client = TelegramClient(MemorySession(), os.environ.get("API_ID"), os.environ.get("API_HASH")).start(bot_token=os.environ.get("BOT_TOKEN"))
bot = Bot(token=os.environ.get("BOT_TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=["start"], run_task=True)
async def akira_start(message: types.Message):
	await message.reply("Hi! Im Akira.")

@dp.message_handler(commands=["ipfs"], run_task=True)
async def akira_ipfs(message: types.Message):
	temp_dir = tempfile.mkdtemp(dir=akira_dir)
	chat = await client.get_entity(message.chat.id)
	telethon_message = await client.get_messages(chat, ids=message.message_id)
	if telethon_message.reply_to_msg_id:
		telethon_reply_message = await client.get_messages(chat, ids=telethon_message.reply_to_msg_id)
		if type(telethon_reply_message.media) == MessageMediaDocument:
			file_size = telethon_reply_message.document.size
		elif type(telethon_reply_message.media) == MessageMediaPhoto:
			file_size = telethon_reply_message.photo.size
		else:
			await message.reply("Invalid file type.")
			shutil.rmtree(temp_dir)
			return
		if file_size > (512 * 1024 * 1024):
			await message.reply("File is too big. Maximum file size is 512 MB.")
			shutil.rmtree(temp_dir)
			return
		reply = await message.reply("Downloading...")
		try:
			downloaded_file = await telethon_reply_message.download_media(temp_dir)
		except:
			await reply.delete()
			await message.reply("An error occurred while downloading a file.")
			shutil.rmtree(temp_dir)
			return
		await reply.edit_text("Uploading...")
		try:
			async with aiohttp.ClientSession() as session:
				response = await session.post("https://ipfsupload.herokuapp.com/upload", data={"file": open(downloaded_file, "rb")})
		except:
			await reply.delete()
			await message.reply("An error occurred while uploading a file.")
			shutil.rmtree(temp_dir)
			return
		await reply.delete()
		await message.reply(await response.text())
	else:
		await message.reply("Please respond to a message with a file.")
	shutil.rmtree(temp_dir)

@dp.message_handler(commands=["yt2a"], run_task=True)
async def akira_yt2a(message: types.Message):
	await message.reply("This command is not available now.")

@dp.message_handler(commands=["weather"], run_task=True)
async def akira_weather(message: types.Message):
	await message.reply("This command is not available now.")

@dp.message_handler(commands=["qr"], run_task=True)
async def akira_qr(message: types.Message):
	await message.reply("This command is not available now.")

@dp.message_handler(commands=["xdl"], run_task=True)
async def akira_xdl(message: types.Message):
	temp_dir = tempfile.mkdtemp(dir=akira_dir)
	args = message.get_args().split(" ")
	chat = await client.get_entity(message.chat.id)
	telethon_message = await client.get_messages(chat, ids=message.message_id)
	async def default_upload(sent, total):
		percent = int(round((sent / total) * 100))
		try:
			if percent == 20:
				await reply.edit_text("Uploading... (This might take a while)\n●○○○○")
			elif percent == 40:
				await reply.edit_text("Uploading... (This might take a while)\n●●○○○")
			elif percent == 60:
				await reply.edit_text("Uploading... (This might take a while)\n●●●○○")
			elif percent == 80:
				await reply.edit_text("Uploading... (This might take a while)\n●●●●○")
		except: pass
	async def default_download(sent, total):
		percent = int(round((sent / total) * 100))
		try:
			if percent == 20:
				await reply.edit_text("Downloading...\n●○○○○")
			elif percent == 40:
				await reply.edit_text("Downloading...\n●●○○○")
			elif percent == 60:
				await reply.edit_text("Downloading...\n●●●○○")
			elif percent == 80:
				await reply.edit_text("Downloading...\n●●●●○")
		except: pass
	if args:
		if args[0] == "animekisa":
			reply = await message.reply("Parsing Fembed ID...")
			async with aiohttp.ClientSession() as session:
				try:
					async with session.get("https://animekisa.tv/pokemon-2019-episode-32") as site:
						fembed_id = None
						async for line in site.content:
							line = line.decode("UTF-8")
							if "var Fembed" in line and "var Fembed2" not in line:
								fembed_id = line.split("\"")[1].split("/")[-1]
				except:
					await reply.delete()
					await message.reply("Failed to parse Fembed ID.")
					return

				try:
					async with session.post(f"https://fcdn.stream/api/source/{fembed_id}") as api:
						videos = (await api.json())["data"]
				except:
					await reply.delete()
					await message.reply("Failed to get a response from API.")
					return

				index = -1
				await reply.edit_text("Downloading...\n○○○○○")
				while True:
					with urllib.request.urlopen(videos[index]["file"]) as video:
						video_size = int(video.info()["Content-Length"])
						if (video_size / 1048576) > 2048:
							index -= 1
							if len(videos) + (index + 1) == 0:
								await reply.delete()
								await message.reply("Video is too big.")
								return
							continue
						async with aiofiles.open(f"{temp_dir}/video.mp4", "wb") as ovideo:
							while True:
								await default_download(await ovideo.tell(), video_size)
								chunk = video.read(65535)
								if not chunk:
									break
								await ovideo.write(chunk)
							break
				await reply.edit_text("Uploading... (This might take a while)\n○○○○○")
				await client.send_file(
					chat,
					file=open(f"{temp_dir}/video.mp4", "rb"),
					reply_to=telethon_message,
					progress_callback=default_upload,
					attributes=[DocumentAttributeVideo(
						duration=0,
						w=0,
						h=0,
						round_message=False,
						supports_streaming=True
					)]
				)
		else:
			await message.reply("Unknown downloader \"{}\".".format(args[0]))
	else:
		await message.reply("Usage: /xdl (downloader) (URL)")
	shutil.rmtree(temp_dir)

if __name__ == "__main__":
	log(f"Starting Akira {akira}...")

	if not os.path.exists(akira_dir):
		os.mkdir(akira_dir)

	async def on_startup(dp): await bot.set_webhook(os.environ.get("URL") + "/" + os.environ.get("BOT_TOKEN"))

	log("Started.")
	start_webhook(
		dispatcher=dp,
		webhook_path="/" + os.environ.get("BOT_TOKEN"),
		on_startup=on_startup,
		port=os.environ.get("PORT")
	)
