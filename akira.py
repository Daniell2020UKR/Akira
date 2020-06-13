import os, json, tempfile, shutil, requests, akira_lang
from youtube_dl import YoutubeDL
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.dispatcher import run_async
from telegram import ChatAction
from PIL import Image

akira = "1.00-alpha"
default_settings = {"token": "", "debug": True}

@run_async
def akira_yt2a(update, context):
	temp_dir = tempfile.mkdtemp(dir=tempfile.gettempdir())
	args = {"format": "bestaudio[filesize<?50M]", "outtmpl": temp_dir + "/audio.%(ext)s"}
	if context.args:
		sent_message = update.message.reply_text(akira_lang.translations["en"]
			["akira_downloading"])
		try:
			audio_info = YoutubeDL(args).extract_info(context.args[0])
		except:
			update.message.reply_text(akira_lang.translations["en"]
				["akira_yt2a_download_error"])
			sent_message.delete()
			shutil.rmtree(temp_dir)
		open(temp_dir + "/cover.jpg", "wb").write(
			requests.get(audio_info["thumbnail"]).content)
		cover_image = Image.open(temp_dir + "/cover.jpg")
		cover_image.thumbnail((320, 320))
		cover_image.save(temp_dir + "/cover.jpg")
		sent_message.edit_text(akira_lang.translations["en"]
			["akira_uploading"])
		try:
			with open(temp_dir + "/audio." + audio_info["ext"], "rb") as audio_file:
				with open(temp_dir + "/cover.jpg", "rb") as cover_file:
					update.message.reply_audio(audio_file,
						title=audio_info["title"],
						performer=audio_info["artist"],
						thumb=cover_file)
		except:
			update.message.reply_text(akira_lang.translations["en"]
				["akira_yt2a_upload_error"])
			sent_message.delete()
			shutil.rmtree(temp_dir)
		sent_message.delete()
	else:
		update.message.reply_text(akira_lang.translations["en"]
			["akira_noargs"])
	shutil.rmtree(temp_dir)

@run_async
def akira_start(update, context):
	update.message.reply_text(akira_lang.translations["en"]
		["akira_start"])

@run_async
def akira_setlang(update, context):
	if context.args:
		pass # Not implemented
	else:
		update.message.reply_text(akira_lang.translations["en"]
			["akira_noargs"])

@run_async
def akira_version(update, context):
	update.message.reply_text(akira_lang.translations["en"]
		["akira_version"] + akira)

if not os.path.exists("settings.json"):
    with open("settings.json", "w") as settings_file:
        settings_file.write(json.dumps(default_settings, indent=4))

with open("settings.json", "r") as settings_file:
    settings = json.loads(settings_file.read())

updater = Updater(settings["token"], use_context=True)
updater.dispatcher.add_handler(CommandHandler("start", akira_start))
updater.dispatcher.add_handler(CommandHandler("yt2a", akira_yt2a))
updater.dispatcher.add_handler(CommandHandler("version", akira_version))
updater.start_polling()
print("Akira started")
