import os, subprocess, shutil, aiohttp, aria2p, time, xdl, tempfile, builtins
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telethon.tl.types import DocumentAttributeVideo, DocumentAttributeAudio
from telethon.sessions import MemorySession
from telethon import TelegramClient
from youtube_dl import YoutubeDL

akira = "0.1"
akira_dir = os.getcwd() + "/akira"

def log(text): print(f"[Akira] {text}")

client = TelegramClient(MemorySession(), os.environ.get("API_ID"), os.environ.get("API_HASH")).start(bot_token=os.environ.get("BOT_TOKEN"))
bot = Bot(token=os.environ.get("BOT_TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())

dots = {
	0: "○○○○○○○○○○",
	10: "●○○○○○○○○○",
	20: "●●○○○○○○○○",
	30: "●●●○○○○○○○",
	40: "●●●●○○○○○○",
	50: "●●●●●○○○○○",
	60: "●●●●●●○○○○",
	70: "●●●●●●●○○○",
	80: "●●●●●●●●○○",
	90: "●●●●●●●●●○",
	100: "●●●●●●●●●●"
}

builtins.yt2a_cache = {}

@dp.message_handler(commands=["start"], run_task=True)
async def akira_start(message: types.Message):
	await message.reply("Hi! Im Akira.")

@dp.message_handler(commands=["weather"], run_task=True)
async def akira_weather(message: types.Message):
	await message.reply("This command is not available now.")

@dp.message_handler(commands=["qr"], run_task=True)
async def akira_qr(message: types.Message):
	await message.reply("This command is not available now.")

@dp.message_handler(commands=["xdl"], run_task=True)
async def akira_xdl(message: types.Message):
	args = message.get_args().split(" ")
	if args[0]:
		temp_dir = tempfile.mkdtemp(dir=akira_dir)
		chat = await client.get_entity(message.chat.id)
		telethon_message = await client.get_messages(chat, ids=message.message_id)

		async def upload_callback(sent, total):
			percent = int((sent / total) * 100)
			try:
				if percent in dots.keys():
					await reply.edit_text("Uploading...\nProgress: {}".format(dots[percent]))
			except:
				pass
		async def download_callback(percent, eta, size, speed):
			try:
				if percent in dots.keys():
					await reply.edit_text("Downloading...\nSize: {}\nETA: {}\nSpeed: {}\nProgress: {}".format(size, eta, speed, dots[percent]))
			except:
				pass

		reply = await message.reply("Downloading...\nProgress: {}".format(dots[0]))
		try:
			ret = await xdl.downloaders[args[0]](aria2client, args[1], temp_dir, download_callback)
		except:
			await message.reply("Downloader \"{}\" is not found.".format(args[0]))
			await reply.delete()
			shutil.rmtree(temp_dir)
			return
		if ret == xdl.xdl_file_too_big:
			await message.reply("The file is too big.")
			await reply.delete()
			shutil.rmtree(temp_dir)
			return
		elif ret == xdl.xdl_download_error:
			await message.reply("An error occurred while downloading file.")
			await reply.delete()
			shutil.rmtree(temp_dir)
			return
		elif ret == xdl.xdl_parse_error:
			await message.reply("An error occurred while parsing info.")
			await reply.delete()
			shutil.rmtree(temp_dir)
			return
		elif ret == xdl.xdl_api_error:
			await message.reply("An error occurred while calling API.")
			await reply.delete()
			shutil.rmtree(temp_dir)
			return
		elif ret == xdl.xdl_invalid_url:
			await message.reply("Invalid URL.")
			await reply.delete()
			shutil.rmtree(temp_dir)
			return
		elif ret == xdl.xdl_unknown_error:
			await message.reply("An unknown error occurred.")
			await reply.delete()
			shutil.rmtree(temp_dir)
			return

		if ret[0] == xdl.xdl_aria2:
			target = temp_dir + "/" + ret[1].name

		ext = target.split(".")[-1]

		if ext in ["mp4", "avi", "mkv"]:
			attrib = [DocumentAttributeVideo(
				duration=0,
				w=0,
				h=0,
				round_message=False,
				supports_streaming=True
			)]
		elif ext in ["m4a", "mp3", "ogg", "flac"]:
			attrib = None
		elif ext in ["jpg", "jpeg", "webp", "png"]:
			attrib = None
		else:
			attrib = None

		await reply.edit_text("Uploading...\nProgress: {}".format(dots[0]))
		await client.send_file(
			chat,
			file=open(target, "rb"),
			reply_to=telethon_message,
			progress_callback=upload_callback,
			attributes=attrib
		)
		await reply.delete()

		if ret[0] == xdl.xdl_aria2:
			ret[1].delete(files=True)

		shutil.rmtree(temp_dir)
	else:
		await message.reply("Usage: /xdl (downloader) (URL)")

@dp.message_handler(commands=["yt2a"], run_task=True)
async def akira_yt2a(message: types.Message):
	args = message.get_args().split(" ")
	if args[0]:
		download_dir = tempfile.mkdtemp(dir=akira_dir)
		args = {"format": "bestaudio[ext=m4a][filesize<?250M]", "outtmpl": f"{download_dir}/audio-%(id)s.%(ext)s", "writethumbnail": True}
		reply = await message.reply("Downloading...")
		try:
			with YoutubeDL(args) as ydl:
				audio_info = ydl.extract_info(args[0], download=False)
				audio_id = audio_info["id"]
				if not yt2a_cache.get(audio_id):
					ydl.download([args[0]])
					if os.path.exists(f"{download_dir}/audio-{audio_id}.webp"): thumbext = "webp"
					else: thumbext = "jpg"
		except:
			await message.reply("Download error.")
			await reply.delete()
			shutil.rmtree(download_dir)
			return
		await reply.edit_text("Uploading...")
		chat = await client.get_entity(message.chat.id)
		try:
			if yt2a_cache.get(audio_id):
				await client.send_file(
					chat,
					yt2a_cache[audio_id],
					reply_to=message.message_id
				)
			else:
				audio_file = await client.upload_file(open(f"{download_dir}/audio-{audio_id}.m4a", "rb"))
				audio_message = await client.send_file(
					chat,
					audio_file,
					thumb=open(f"{download_dir}/audio-{audio_id}.{thumbext}", "rb"),
					reply_to=message.message_id,
					attributes=[DocumentAttributeAudio(
						title=audio_info["title"],
						performer=audio_info["artist"],
						voice=True,
						duration=audio_info["duration"]
					)]
				)
				yt2a_cache[audio_id] = audio_message.media
		except:
			await message.reply("Upload error.")
			await reply.delete()
			shutil.rmtree(download_dir)
			return
		await reply.delete()
		shutil.rmtree(download_dir)
	else:
		await message.reply("No arguments.")

if __name__ == "__main__":
	log(f"Starting Akira {akira}...")

	log("Starting Aria2 daemon...")
	aria2proc = subprocess.Popen(["aria2c", "--enable-rpc"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
	time.sleep(1)

	log("Creating Aria2 client...")
	aria2client = aria2p.API(aria2p.Client(host="http://127.0.0.1", port=6800))

	if not os.path.exists(akira_dir):
		os.mkdir(akira_dir)

	async def on_startup(dp):
		await bot.set_webhook(os.environ.get("URL") + "/" + os.environ.get("BOT_TOKEN"))

	log("Started.")
	start_webhook(
		dispatcher=dp,
		webhook_path="/" + os.environ.get("BOT_TOKEN"),
		on_startup=on_startup,
		port=os.environ.get("PORT")
	)
