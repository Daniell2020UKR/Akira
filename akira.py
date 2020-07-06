import os, asyncio, random, qrcode, tempfile, shutil, uuid
from nanogram import Nanogram

akira = '1.0'

akira_emotion_list = [
	'CAACAgEAAxkBAAIFOV8DEObNjlBhpCutq4wXnqbrfjyiAAKxcgACrxliB5TVrEn25LatGgQ', # Happy
	'CAACAgEAAxkBAAIFOl8DEPRjVNUR-yHQiZqQb3l44N1SAAKycgACrxliB51RDc5Wr2auGgQ', # "Heya!" sticker
	'CAACAgEAAxkBAAIFO18DEQucDJDuoPXtTld5aHhNgZKiAAKzcgACrxliB8RVY-WhFab7GgQ', # Sad
	'CAACAgEAAxkBAAIFPF8DERvXwj1MFYl8mIQjGy5AkJOkAAK0cgACrxliBw27i49II75TGgQ', # Excited
	'CAACAgEAAxkBAAIFPV8DEWMj0anyldeCkqH-vKcQLspIAAK1cgACrxliBz_n4xaSDXdsGgQ', # Confused
	'CAACAgEAAxkBAAIFPl8DEXari6m0XAmsZnQTJUZZrs7pAAK2cgACrxliB0Nvze67_rYGGgQ', # Blushing
	'CAACAgEAAxkBAAIFP18DEY8mTCzF91HUtqY1guH4ZJQEAAK3cgACrxliBygb2swZUQI_GgQ', # Extremly blushing
	'CAACAgEAAxkBAAIFQF8DEai-DSojPkooTXYBW2JYH8lpAAK4cgACrxliB6lN16aqL4XTGgQ', # Yawn
	'CAACAgEAAxkBAAIFQV8DEb5GbCBRaXCpLVOBHLGh18FAAAK5cgACrxliB7KwP472kZ29GgQ', # Annoyed
	'CAACAgEAAxkBAAIFQl8DEdOosPJ16inmoF-dAAGWPvC5lQACM3wAAq8ZYgcNwiff8AmGtxoE', # A N G E R Y
	'CAACAgEAAxkBAAIFQ18DEeW8Tm9FKBF-stW_duOdgVIJAAK6cgACrxliB3-dKoMlIhFWGgQ' # Confident
]

def log(text): print(f'[Akira] {text}')

log(f'Starting Akira {akira}...')

log('Creating bot client...')
bot = Nanogram(os.environ.get('BOT_TOKEN'))

log('Creating temporary directory...')
temp_dir = tempfile.gettempdir() + '/akira'
if os.path.exists(temp_dir):
	shutil.rmtree(temp_dir)
os.mkdir(temp_dir)

async def akira_emotion(bot, update):
	index = random.randint(0, len(akira_emotion_list) - 1)
	await bot.send_sticker(
		akira_emotion_list[index],
		chat_id=update['message']['chat']['id'],
		reply_to_message_id=update['message']['message_id']
	)

async def akira_qr(bot, update):
	if update['message']['args']:
		qrid = uuid.uuid4()
		qr = qrcode.make(' '.join(update['message']['args']))
		qr.save(f'{temp_dir}/qr-{qrid}.jpg')
		await bot.send_photo(
			open(f'{temp_dir}/qr-{qrid}.jpg', 'rb'),
			chat_id=update['message']['chat']['id'],
			reply_to_message_id=update['message']['message_id']
		)
		os.remove(f'{temp_dir}/qr-{qrid}.jpg')
	else:
		await bot.send_message(
			'No arguments.',
			chat_id=update['message']['chat']['id'],
			reply_to_message_id=update['message']['message_id']
		)

async def akira_start(bot, update):
	await bot.send_message(
		'Hi! Im Akira.',
		chat_id=update['message']['chat']['id'],
		reply_to_message_id=update['message']['message_id']
	)

bot.add_command('/emotion', akira_emotion)
bot.add_command('/start', akira_start)
bot.add_command('/qr', akira_qr)
bot.delete_webhook()
bot.set_webhook(os.environ.get('URL'), os.environ.get('PORT'))
log('Started.')
bot.start_webhook()
