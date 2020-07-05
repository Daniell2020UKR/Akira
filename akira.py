import os, asyncio, tempfile, shutil
from telethon import TelegramClient, events
from telethon.sessions import MemorySession
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo
from telegram.ext import Updater
from youtube_dl import YoutubeDL

akira = '1.0.0-alpha'

def log(text): print(f'[Akira] {text}')

def get_args(event):
    args = event.text.split(' ')
    args.pop(0)
    return args

log(f'Starting Akira {akira}...')

log('Creating bot client...')
client = TelegramClient(MemorySession(), os.environ.get('API_ID'), os.environ.get('API_HASH')).start(bot_token=os.environ.get('BOT_TOKEN'))
updater = Updater(os.environ.get('BOT_TOKEN'), use_context=True)
updater.start_webhook(listen='0.0.0.0', port=os.environ.get('PORT'), url_path=os.environ.get('BOT_TOKEN'))
updater.bot.set_webhook(os.environ.get('URL') + '/' + os.environ.get('BOT_TOKEN'))

log('Creating functions...')
@client.on(events.NewMessage(pattern='/start'))
async def akira_start(event):
    await event.reply('Hi! Im Akira.')

@client.on(events.NewMessage(pattern='/help'))
async def akira_help(event):
    await event.reply('Help is currently unavailable.')

@client.on(events.NewMessage(pattern='/version'))
async def akira_version(event):
    await event.reply(f'My version - {akira}.')

@client.on(events.NewMessage(pattern='/donate'))
async def akira_donate(event):
    await event.reply('Donate - @Myst33dDonate')

@client.on(events.NewMessage(pattern='/yt2a'))
async def akira_yt2a(event):
	args = get_args(event)
	if args:
		temp_dir = tempfile.mkdtemp(dir=tempfile.gettempdir())
		dargs = {'format': 'bestaudio[ext=m4a][filesize<?250M]', 'outtmpl': f'{temp_dir}/audio-%(id)s.%(ext)s', 'writethumbnail': True}
		sent_message = await event.reply('Downloading...')
		try:
			audio_info = YoutubeDL(dargs).extract_info(args[0])
			id = audio_info['id']
			if os.path.exists(f'{temp_dir}/audio-{id}.webp'): thumbext = 'webp'
			else: thumbext = 'jpg'
		except:
			await event.reply('Download error.')
			await sent_message.delete()
			shutil.rmtree(temp_dir)
			return
		await sent_message.edit('Uploading...')
		try:
			audio_file = await client.upload_file(open(f'{temp_dir}/audio-{id}.m4a', 'rb'))
			await client.send_file(
				event.chat,
				audio_file,
				thumb=open(f'{temp_dir}/audio-{id}.{thumbext}', 'rb'),
				reply_to=event.message,
				attributes=[DocumentAttributeAudio(
					title=audio_info['title'],
					performer=audio_info['artist'],
					voice=True,
					duration=audio_info['duration']
				)]
			)
		except:
			await event.reply('Upload error.')
			await sent_message.delete()
			shutil.rmtree(temp_dir)
			return
		await sent_message.delete()
		shutil.rmtree(temp_dir)	
	else:
		await event.reply('No arguments supplied.')

log('Started.')
client.run_until_disconnected()
