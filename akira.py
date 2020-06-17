import os, json, tempfile, shutil, akira_lang
from youtube_dl import YoutubeDL
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram import ChatAction, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image

akira = "1.01-alpha"
default_settings = {"token": "", "debug": True}

def get_lang(context):
	try: return context.chat_data["lang"]
	except: return "en"

def is_authorized(update, context):
	# Not yet
	user = context.bot.get_chat_member(update.message.chat.id, update.message.from_user.id)
	print(user)

@run_async
def akira_yt2a(update, context):
	# Honestly, this function can be implemented in a better way
	if context.args:
		temp_dir = tempfile.mkdtemp(dir=tempfile.gettempdir())
		args = {"format": "bestaudio[ext=m4a][filesize<?50M]/bestaudio[ext=webm][filesize<?50M]", "outtmpl": f"{temp_dir}/audio-%(id)s.%(ext)s", "noplaylist": True, "playliststart": 1, "playlistend": 20, "writethumbnail": True}
		sent_message = update.message.reply_text(akira_lang.translations
			[get_lang(context)]["akira_downloading"])
		try:
			audio_info = YoutubeDL(args).extract_info(context.args[0])
			try:
				if audio_info["_type"] == "playlist":
					vid = []
					for i in audio_info["entries"]:
						vid.append((i["id"], i["playlist_index"] - 1))
			except:
				audioext = audio_info["ext"]
		except:
			update.message.reply_text(akira_lang.translations
				[get_lang(context)]["akira_yt2a_download_error"])
			sent_message.delete()
			shutil.rmtree(temp_dir)
			return
		sent_message.edit_text(akira_lang.translations
			[get_lang(context)]["akira_uploading"])
		try:
			try:
				if audio_info["_type"] == "playlist":
					for i in vid:
						index = i[1]
						id = i[0]
						artist = audio_info["entries"][index]["artist"]
						title = audio_info["entries"][index]["title"]
						audioext = audio_info["entries"][index]["ext"]
						if os.path.exists(f"{temp_dir}/audio-{id}.jpg"):
							thumbext = "jpg"
							Image.open(f"{temp_dir}/audio-{id}.jpg").convert("RGB").save(f"{temp_dir}/audio-{id}.jpg")
						else:
							thumbext = "webp"
							Image.open(f"{temp_dir}/audio-{id}.webp").convert("RGB").save(f"{temp_dir}/audio-{id}.jpg")
						update.message.reply_audio(open(f"{temp_dir}/audio-{id}.{audioext}", "rb"),
							title=title,
							performer=artist,
							thumb=open(f"{temp_dir}/audio-{id}.{thumbext}", "rb"))
			except:
				id = audio_info["id"]
				if os.path.exists(f"{temp_dir}/audio-{id}.jpg"):
					thumbext = "jpg"
					Image.open(f"{temp_dir}/audio-{id}.jpg").convert("RGB").save(f"{temp_dir}/audio-{id}.jpg")
				else:
					thumbext = "webp"
					Image.open(f"{temp_dir}/audio-{id}.webp").convert("RGB").save(f"{temp_dir}/audio-{id}.jpg")
				update.message.reply_audio(open(f"{temp_dir}/audio-{id}.{audioext}", "rb"),
						title=audio_info["title"],
						performer=audio_info["artist"],
						thumb=open(f"{temp_dir}/audio-{id}.{thumbext}", "rb"))
		except:
			update.message.reply_text(akira_lang.translations
				[get_lang(context)]["akira_yt2a_upload_error"])
			sent_message.delete()
			shutil.rmtree(temp_dir)
			return
		sent_message.delete()
		shutil.rmtree(temp_dir)
	else:
		update.message.reply_text(akira_lang.translations
			[get_lang(context)]["akira_noargs"])

@run_async
def akira_start(update, context):
	update.message.reply_text(akira_lang.translations
		[get_lang(context)]["akira_start"])

@run_async
def akira_version(update, context):
	update.message.reply_text(akira_lang.translations
		[get_lang(context)]["akira_version"] + akira)

@run_async
def akira_setlang(update, context):
	if context.args:
		if context.args[0] in akira_lang.available_lang:
			context.chat_data["lang"] = context.args[0]
			update.message.reply_text(akira_lang.translations
				[get_lang(context)]["akira_setlang"])
		else:
			update.message.reply_text(akira_lang.translations
				[get_lang(context)]["akira_nolang"])
	else:
		update.message.reply_text(akira_lang.translations
			[get_lang(context)]["akira_noargs"])

@run_async
def akira_logger(update, context):
	# Logging for dev chat(chat id censored on Github)
	if update.message.chat.id == 0:
		print(update.message)

@run_async
def akira_reminder(update, context):
	# Not yet
	context.user_data["captcha_" + update.message.chat.username] = \
		context.job_queue.run_once(akira_debug_job,
			5,
			context=(update, context))
	update.message.reply_text("Job set")

@run_async
def akira_debug_job(context):
	# Not yet
	update, context = context.job.context
	context.bot.send_message(update.message.chat.id,
		"Trigger[\u200b](tg://user?id={})".format(update.message.from_user.id),
		ParseMode.MARKDOWN_V2)

@run_async
def akira_captcha(update, context):
	# Not yet
	pass

if not os.path.exists("settings.json"):
    with open("settings.json", "w") as settings_file:
        settings_file.write(json.dumps(default_settings, indent=4))

with open("settings.json", "r") as settings_file:
    settings = json.loads(settings_file.read())

updater = Updater(settings["token"], use_context=True)
updater.dispatcher.add_handler(CommandHandler("start", akira_start))
updater.dispatcher.add_handler(CommandHandler("yt2a", akira_yt2a))
updater.dispatcher.add_handler(CommandHandler("version", akira_version))
updater.dispatcher.add_handler(CommandHandler("setlang", akira_setlang))
#updater.dispatcher.add_handler(CommandHandler("debug", akira_debug))
#updater.dispatcher.add_handler(CommandHandler("captcha", akira_captcha))
updater.dispatcher.add_handler(MessageHandler(Filters.all, akira_logger))
updater.start_polling()
print("Akira started")
