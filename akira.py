# Please destroy this fucking awful bot, i wanna die from looking at this awful code.
# And yes, this is a monolithic bot, aka fucking awful bot with no modules support.

import os, subprocess, shutil, aiohttp, aria2p, time, xdl, tempfile, builtins
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telethon.tl.types import DocumentAttributeAudio
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

# Ass
builtins.yt2a_cache = {}
builtins.sc2a_cache = {}

async def upload_callback(sent, total):
	percent = int((sent / total) * 100)
	try:
		if percent in dots.keys():
			await reply.edit_text("Uploading...\nProgress: {}".format(dots[percent]))
	except:
		pass

@dp.message_handler(commands=["start"], run_task=True)
async def akira_start(message: types.Message):
	await message.reply("Hi! Im Akira.")

@dp.message_handler(commands=["xdl"], run_task=True)
async def akira_xdl(message: types.Message):		# Shitty fucking piss dickhead motherfucker ugly ass goblin, fuck this shit.
	args = message.get_args().split(" ")
	if args[0]:
		temp_dir = tempfile.mkdtemp(dir=akira_dir)
		chat = await client.get_entity(message.chat.id)
		telethon_message = await client.get_messages(chat, ids=message.message_id)

		reply = await message.reply("Downloading...\nProgress: {}".format(dots[0]))

		async def download_callback(percent, eta, size, speed):
			try:
				if percent in dots.keys():
					await reply.edit_text("Downloading...\nSize: {}\nETA: {}\nSpeed: {}\nProgress: {}".format(size, eta, speed, dots[percent]))
			except: pass

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
async def akira_yt2a(message: types.Message):		# THIS SHIT DOESNT WORK HOW ITS SUPPOSED TO, WHY????????
	args = message.get_args()
	if args:
		download_dir = tempfile.mkdtemp(dir=akira_dir)
		dargs = {"format": "bestaudio[ext=m4a][filesize<?2000M]/bestaudio[ext=webm][filesize<?2000M]", "outtmpl": f"{download_dir}/audio-%(id)s.%(ext)s", "writethumbnail": True}
		reply = await message.reply("Downloading...")
		try:
			with YoutubeDL(dargs) as ydl:
				audio_info = ydl.extract_info(args, download=False)
				audio_id = audio_info["id"]
				audio_ext = audio_info["ext"]
				if not yt2a_cache.get(audio_id):
					ydl.download([args])
					if os.path.exists(f"{download_dir}/audio-{audio_id}.webp"):
						thumbext = "webp"
					else:
						thumbext = "jpg"
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
				audio_message = await client.send_file(
					chat,
					open(f"{download_dir}/audio-{audio_id}.{audio_ext}", "rb"),
					thumb=open(f"{download_dir}/audio-{audio_id}.{thumbext}", "rb"),
					reply_to=message.message_id,
					attributes=[DocumentAttributeAudio(
						title=audio_info["title"],
						performer=audio_info["uploader"],
						duration=int(audio_info["duration"]) # In case somebody goes monkey brain we have int() (refer to /sc2a function)
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

@dp.message_handler(commands=["sc2a"], run_task=True)
async def akira_sc2a(message: types.Message):		# Also fuck this thing too, inherits all horrible code from /yt2a
	args = message.get_args()
	if args:
		download_dir = tempfile.mkdtemp(dir=akira_dir)
		dargs = {"format": "bestaudio[filesize<?2000M]", "outtmpl": f"{download_dir}/audio-%(id)s.%(ext)s", "writethumbnail": True}
		reply = await message.reply("Downloading...")
		try:
			with YoutubeDL(dargs) as ydl:
				audio_info = ydl.extract_info(args, download=False)
				audio_id = audio_info["id"]
				audio_ext = audio_info["ext"]
				if not sc2a_cache.get(audio_id):
					ydl.download([args])
		except:
			await message.reply("Download error.")
			await reply.delete()
			shutil.rmtree(download_dir)
			return
		await reply.edit_text("Uploading...")
		chat = await client.get_entity(message.chat.id)
		try:
			if sc2a_cache.get(audio_id):
				await client.send_file(
					chat,
					sc2a_cache[audio_id],
					reply_to=message.message_id
				)
			else:
				audio_message = await client.send_file(
					chat,
					open(f"{download_dir}/audio-{audio_id}.{audio_ext}", "rb"),
					thumb=open(f"{download_dir}/audio-{audio_id}.jpg", "rb"),
					reply_to=message.message_id,
					attributes=[DocumentAttributeAudio(
						title=audio_info["title"],
						performer=audio_info["uploader"],
						duration=int(audio_info["duration"]) # Whoever coded Soundcloud extractor, fuck you. WHY IS IT FUCKING FLOAT INSTEAD OF INT
					)]
				)
				sc2a_cache[audio_id] = audio_message.media
		except:
			await message.reply("Upload error.")
			await reply.delete()
			shutil.rmtree(download_dir)
			return
		await reply.delete()
		shutil.rmtree(download_dir)
	else:
		await message.reply("No arguments.")

@dp.message_handler(commands=["weather"], run_task=True)
async def akira_weather(message: types.Message):
	args = message.get_args()
	if args:
		if os.environ.get("OWM_API_KEY"):
			api_key = os.environ.get("OWM_API_KEY")
			async with aiohttp.ClientSession() as session:
				async with session.get(f"https://api.openweathermap.org/data/2.5/weather?q={args}&units=metric&appid={api_key}") as response:
					weather_data = await response.json()
			try:
				# I know, this is a bad way to do this, but format strings are fucking awful, so i cant do it any other way.
				country = weather_data["sys"]["country"]
				condition = weather_data["weather"][0]["main"]
				condition_description = weather_data["weather"][0]["description"]
				city = weather_data["name"]
				temp = weather_data["main"]["temp"]
				max_temp = weather_data["main"]["temp_max"]
				min_temp = weather_data["main"]["temp_min"]
				feel_temp = weather_data["main"]["feels_like"]
				wind_speed = weather_data["wind"]["speed"]
				humidity = weather_data["main"]["humidity"]
			except:
				await message.reply("An error occurred while trying to get weather data.")
				return
			await message.reply(
				f"=== {country}, {city} ===\n"
				f"Condition: {condition}({condition_description})\n"
				f"Humidity: {humidity}%\n"
				f"Wind speed: {wind_speed} m/s\n\n"
				f"=== Temperature ===\n"
				f"Current: {temp} °C\n"
				f"Feels like: {feel_temp} °C\n"
				f"Max: {max_temp} °C\n"
				f"Min: {min_temp} °C\n"
			)
		else:
			await message.reply("No OpenWeatherMap API key is found.")
	else:
		await message.reply("No arguments.")

@dp.message_handler(commands=["kanye"], run_task=True)
async def akira_kanye(message: types.Message):
	async with aiohttp.ClientSession() as session:
		async with session.get("https://api.kanye.rest") as response:
			await message.reply((await response.json())["quote"])

@dp.message_handler(commands=["joke"], run_task=True)
async def akira_joke(message: types.Message):
	async with aiohttp.ClientSession() as session:
		async with session.get("https://sv443.net/jokeapi/v2/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist&format=txt") as response:
			await message.reply(await response.text())

if __name__ == "__main__":
	log(f"Starting Akira {akira}...")

	# Is this a good thing to do? I dont know.
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
