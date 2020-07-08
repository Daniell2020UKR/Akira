import os, asyncio, random, qrcode, tempfile, shutil, uuid
from telethon.sessions import MemorySession
from telethon.tl.types import DocumentAttributeAudio
from telethon import TelegramClient
from nanogram import Nanogram
from pyzbar.pyzbar import decode
from PIL import Image
from youtube_dl import YoutubeDL

akira = '0.1'

def log(text): print(f'[Akira] {text}')

log(f'Starting Akira {akira}...')

log('Creating bot client...')
client = TelegramClient(MemorySession(), os.environ.get('API_ID'), os.environ.get('API_HASH')).start(bot_token=os.environ.get('BOT_TOKEN'))
bot = Nanogram(os.environ.get('BOT_TOKEN'))

log('Creating temporary directory...')
temp_dir = tempfile.gettempdir() + '/akira'
if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
os.mkdir(temp_dir)

async def akira_qr(bot, update):
	if update['message'].get('reply_to_message'):
		if update['message']['reply_to_message'].get('text') or update['message']['reply_to_message'].get('caption'):
			text = update['message']['reply_to_message'].get('text') or update['message']['reply_to_message'].get('caption')
			qrid = uuid.uuid4()
			qr = qrcode.make(text)
			qr.save(f'{temp_dir}/qr-{qrid}.jpg')
			await bot.send_photo(
				photo=open(f'{temp_dir}/qr-{qrid}.jpg', 'rb'),
				chat_id=update['message']['chat']['id'],
				reply_to_message_id=update['message']['message_id']
			)
			os.remove(f'{temp_dir}/qr-{qrid}.jpg')
		elif update['message']['reply_to_message'].get('photo'):
			file_path = await bot.download_file(temp_dir, update['message']['reply_to_message']['photo'][0]['file_id'])
			codes = decode(Image.open(file_path))
			response_text = ''
			for code in codes:
				if code.type == 'QRCODE':
					response_text += 'QR Code:\n'
				elif code.type == 'EAN13' or code.type == 'CODE128':
					response_text += 'Bar Code:\n'
				else:
					response_text += 'Unknown Code:\n'
				response_text += '{}\n'.format(code.data.decode('utf-8'))
			if response_text:
				await bot.send_message(
					text=response_text,
					chat_id=update['message']['chat']['id'],
					reply_to_message_id=update['message']['message_id']
				)
			else:
				await bot.send_message(
					text='No QR/bar codes found',
					chat_id=update['message']['chat']['id'],
					reply_to_message_id=update['message']['message_id']
				)
			os.remove(file_path)
		else:
			await bot.send_message(
				text='No photo found',
				chat_id=update['message']['chat']['id'],
				reply_to_message_id=update['message']['message_id']
			)
	elif update['message']['args']:
		qrid = uuid.uuid4()
		qr = qrcode.make(' '.join(update['message']['args']))
		qr.save(f'{temp_dir}/qr-{qrid}.jpg')
		await bot.send_photo(
			photo=open(f'{temp_dir}/qr-{qrid}.jpg', 'rb'),
			chat_id=update['message']['chat']['id'],
			reply_to_message_id=update['message']['message_id']
		)
		os.remove(f'{temp_dir}/qr-{qrid}.jpg')
	elif update['message'].get('photo'):
		file_path = await bot.download_file(temp_dir, update['message']['photo'][0]['file_id'])
		codes = decode(Image.open(file_path))
		response_text = ''
		for code in codes:
			if code.type == 'QRCODE':
				response_text += 'QR Code:\n'
			elif code.type == 'EAN13' or code.type == 'CODE128':
				response_text += 'Bar Code:\n'
			else:
				response_text += 'Unknown Code:\n'
			response_text += '{}\n'.format(code.data.decode('utf-8'))
		if response_text:
			await bot.send_message(
				text=response_text,
				chat_id=update['message']['chat']['id'],
				reply_to_message_id=update['message']['message_id']
			)
		else:
			await bot.send_message(
				text='No QR/bar codes found',
				chat_id=update['message']['chat']['id'],
				reply_to_message_id=update['message']['message_id']
			)
		os.remove(file_path)
	else:
		await bot.send_message(
			text='No arguments.',
			chat_id=update['message']['chat']['id'],
			reply_to_message_id=update['message']['message_id']
		)

async def akira_yt2a(bot, update):
	if update['message']['args']:
		if not bot.bot_data.get('ytdl'): bot.bot_data['ytdl'] = {'audio': {}}
		download_dir = tempfile.mkdtemp(dir=temp_dir)
		args = {'format': 'bestaudio[ext=m4a][filesize<?250M]', 'outtmpl': f'{download_dir}/audio-%(id)s.%(ext)s', 'writethumbnail': True}
		sent_message = await bot.send_message(
			text='Downloading...',
			chat_id=update['message']['chat']['id'],
			reply_to_message_id=update['message']['message_id']
		)
		try:
			with YoutubeDL(args) as ydl:
				audio_info = ydl.extract_info(update['message']['args'][0], download=False)
				id = audio_info['id']
				if not bot.bot_data['ytdl']['audio'].get(id):
					ydl.download([update['message']['args'][0]])
					if os.path.exists(f'{download_dir}/audio-{id}.webp'): thumbext = 'webp'
					else: thumbext = 'jpg'
		except:
			await bot.send_message(
				text='Download error',
				chat_id=update['message']['chat']['id'],
				reply_to_message_id=update['message']['message_id']
			)
			await bot.delete_message(
				chat_id=update['message']['chat']['id'],
				message_id=sent_message['message_id']
			)
			shutil.rmtree(download_dir)
			return
		sent_message = await bot.edit_message(
			text='Uploading...',
			chat_id=update['message']['chat']['id'],
			message_id=sent_message['message_id'],
		)
		chat = await client.get_entity(int(update['message']['chat']['id']))
		try:
			if bot.bot_data['ytdl']['audio'].get(id):
				await client.send_file(
					chat,
					bot.bot_data['ytdl']['audio'][id],
					reply_to=int(update['message']['message_id'])
				)
			else:
				audio_file = await client.upload_file(open(f'{download_dir}/audio-{id}.m4a', 'rb'))
				audio_message = await client.send_file(
					chat,
					audio_file,
					thumb=open(f'{download_dir}/audio-{id}.{thumbext}', 'rb'),
					reply_to=int(update['message']['message_id']),
					attributes=[DocumentAttributeAudio(
						title=audio_info['title'],
						performer=audio_info['artist'],
						voice=True,
						duration=audio_info['duration']
					)]
				)
				bot.bot_data['ytdl']['audio'][id] = audio_message.media
		except:
			await bot.send_message(
				text='Upload error',
				chat_id=update['message']['chat']['id'],
				reply_to_message_id=update['message']['message_id']
			)
			await bot.delete_message(
				chat_id=update['message']['chat']['id'],
				message_id=sent_message['message_id']
			)
			shutil.rmtree(download_dir)
			return
		await bot.delete_message(
			chat_id=update['message']['chat']['id'],
			message_id=sent_message['message_id']
		)
		shutil.rmtree(download_dir)
	else:
		await bot.send_message(
			text='No arguments.',
			chat_id=update['message']['chat']['id'],
			reply_to_message_id=update['message']['message_id']
		)

async def akira_start(bot, update):
	await bot.send_message(
		text='Hi! Im Akira.',
		chat_id=update['message']['chat']['id'],
		reply_to_message_id=update['message']['message_id']
	)

async def akira_weather(bot, update):
	if update['message']['args']:
		if os.environ.get('OWM_API_KEY'):
			api_key = os.environ.get('OWM_API_KEY')
			location = ' '.join(update['message']['args'])
			async with bot.session.get(f'https://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={api_key}') as response:
				weather_data = await response.json()
			try:
				country = weather_data['sys']['country']
				condition = weather_data['weather'][0]['main']
				condition_description = weather_data['weather'][0]['description']
				city = weather_data['name']
				temp = weather_data['main']['temp']
				max_temp = weather_data['main']['temp_max']
				min_temp = weather_data['main']['temp_min']
				feel_temp = weather_data['main']['feels_like']
				wind_speed = weather_data['wind']['speed']
				humidity = weather_data['main']['humidity']
			except:
				await bot.send_message(
					text='An error occurred while trying to get weather data.',
					chat_id=update['message']['chat']['id'],
					reply_to_message_id=update['message']['message_id']
				)
				return
			await bot.send_message(
				text=f'=== {country}, {city} ===\n'
				f'Condition: {condition}, {condition_description}\n'
				f'Humidity: {humidity}%\n'
				f'Wind speed: {wind_speed} m/s\n\n'
				f'=== Temperature ===\n'
				f'Current: {temp} °C\n'
				f'Feels like: {feel_temp} °C\n'
				f'Max: {max_temp} °C\n'
				f'Min: {min_temp} °C\n',
				chat_id=update['message']['chat']['id'],
				reply_to_message_id=update['message']['message_id']
			)
		else:
			await bot.send_message(
				text='No OpenWeatherMap API key is found.',
				chat_id=update['message']['chat']['id'],
				reply_to_message_id=update['message']['message_id']
			)
	else:
		await bot.send_message(
			text='No arguments.',
			chat_id=update['message']['chat']['id'],
			reply_to_message_id=update['message']['message_id']
		)

bot.add_command('/start', akira_start)
bot.add_command('/qr', akira_qr)
bot.add_command('/yt2a', akira_yt2a)
bot.add_command('/weather', akira_weather)
bot.delete_webhook()
bot.set_webhook(os.environ.get('URL'), os.environ.get('PORT'), heroku=True)
log('Started.')
bot.start_webhook()
