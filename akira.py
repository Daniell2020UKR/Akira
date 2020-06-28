import os, asyncio, pymongo, akira_lang, tempfile, shutil, threading
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.contacts import AddContactRequest
from telethon.tl.types import DocumentAttributeAudio
from youtube_dl import YoutubeDL
from akira_db import *
from http.server import BaseHTTPRequestHandler, HTTPServer

akira = '1.0-alpha'

def log(text): print(f'[Akira] {text}')

def get_args(event):
    args = event.text.split(' ')
    args.pop(0)
    return args

def get_lang(chat):
    global chat_data
    if db_find(chat_data, f'{chat.id}_lang'): return db_find(chat_data, f'{chat.id}_lang')['value']
    else: return 'en'

log(f'Starting Akira {akira}...')
log('Getting credentials...')
api_id = os.getenv('API_ID') or ''
api_hash = os.getenv('API_HASH') or ''
mdb_host = os.getenv('MDB_HOST') or ''
if not api_id or not api_hash or not mdb_host:
    log('Seems like some environment variables are not set. Make sure that API_ID, API_HASH and MDB_HOST are set.')
    exit()

log('Connecting to MongoDB server...')
mdb_server = pymongo.MongoClient(mdb_host)['akira']
cred_data = mdb_server['cred']
user_data = mdb_server['user']
chat_data = mdb_server['chat']

log('Creating client entity...')
client = TelegramClient(StringSession(db_find(cred_data, 'authkey')['value']), api_id, api_hash).start()

log('Removing credentials from memory for security...')
api_id = None
api_hash = None
mdb_host = None
del os.environ['API_ID'], os.environ['API_HASH'], os.environ['MDB_HOST']
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
mdb_host = os.getenv('MDB_HOST')
if api_id or api_hash or mdb_host:
    log('Credentials are still accessible.')
    exit()

log('Creating functions...')
@client.on(events.NewMessage(pattern=r'\.start'))
async def akira_start(event):
    chat = await event.get_chat()
    await event.reply(akira_lang.translations[get_lang(chat)]['akira_start'])

@client.on(events.NewMessage(pattern=r'\.help'))
async def akira_help(event):
    chat = await event.get_chat()
    await event.reply(akira_lang.translations[get_lang(chat)]['akira_help'])

@client.on(events.NewMessage(pattern=r'\.version'))
async def akira_version(event):
    chat = await event.get_chat()
    await event.reply(akira_lang.translations[get_lang(chat)]['akira_version'] + akira)

@client.on(events.NewMessage(pattern=r'\.donate'))
async def akira_donate(event):
    chat = await event.get_chat()
    await event.reply(akira_lang.translations[get_lang(chat)]['akira_donate'])

@client.on(events.NewMessage(pattern=r'\.addme'))
async def akira_addme(event):
    chat = await event.get_chat()
    sender = await event.get_sender()
    if event.is_private:
        await client(AddContactRequest(
            id=sender.id,
            first_name=sender.first_name,
            last_name=sender.last_name or '',
            phone=sender.phone or ''
        ))
        await event.reply(akira_lang.translations[get_lang(chat)]['akira_newcontact'])
    else:
        await event.reply(akira_lang.translations[get_lang(chat)]['akira_pmonly'])

@client.on(events.NewMessage(pattern=r'\.setlang'))
async def akira_setlang(event):
    chat = await event.get_chat()
    args = get_args(event)
    if args:
        if args[0] in akira_lang.translations.keys():
            if db_find(chat_data, f'{chat.id}_lang'):
                db_update(chat_data, f'{chat.id}_lang', args[0])
                await event.reply(akira_lang.translations[get_lang(chat)]['akira_newlang'])
            else:
                db_insert(chat_data, f'{chat.id}_lang', args[0])
                await event.reply(akira_lang.translations[get_lang(chat)]['akira_newlang'])
        else:
            await event.reply(akira_lang.translations[get_lang(chat)]['akira_nolang'])
    else:
        await event.reply(akira_lang.translations[get_lang(chat)]['akira_noargs'])

@client.on(events.NewMessage(pattern=r'\.yt2a'))
async def akira_yt2a(event):
    chat = await event.get_chat()
    args = get_args(event)
    if args:
        async def upload_callback(current, total):
            uploading_string = akira_lang.translations[get_lang(chat)]['akira_uploading']
            uploaded = round(current / 1024000, 2)
            filesize = round(total / 1024000, 2)
            await sent_message.edit(f'{uploading_string} {uploaded}/{filesize} MB')
        temp_dir = tempfile.mkdtemp(dir=tempfile.gettempdir())
        dargs = {'format': 'bestaudio[ext=m4a][filesize<?200M]', 'outtmpl': f'{temp_dir}/audio-%(id)s.%(ext)s', 'writethumbnail': True}
        sent_message = await event.reply(akira_lang.translations[get_lang(chat)]['akira_downloading'])
        try:
            audio_info = YoutubeDL(dargs).extract_info(args[0])
            id = audio_info['id']
            if os.path.exists(f'{temp_dir}/audio-{id}.webp'):
                thumbext = 'webp'
            else:
                thumbext = 'jpg'
        except:
            await event.reply(akira_lang.translations[get_lang(chat)]['akira_audio_download_error'])
            await sent_message.delete()
            shutil.rmtree(temp_dir)
            return
        await sent_message.edit(akira_lang.translations[get_lang(chat)]['akira_uploading'])
        try:
            await client.send_file(
                chat,
                file=open(f'{temp_dir}/audio-{id}.m4a', 'rb'),
                thumb=open(f'{temp_dir}/audio-{id}.{thumbext}', 'rb'),
                reply_to=event.message,
                progress_callback=upload_callback,
                attributes=[DocumentAttributeAudio(
                    title=audio_info['title'],
                    performer=audio_info['artist'],
                    voice=True,
                    duration=audio_info['duration']
                )]
            )
        except:
            await event.reply(akira_lang.translations[get_lang(chat)]['akira_audio_upload_error'])
            await sent_message.delete()
            shutil.rmtree(temp_dir)
            return
        await sent_message.delete()
        shutil.rmtree(temp_dir)
    else:
        await event.reply(akira_lang.translations[get_lang(chat)]['akira_noargs'])


if os.getenv('PORT'):
    log('Heroku detected, binding PORT...')
    def heroku_binder():
        class Binder(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('Akira on Heroku!'.encode('utf-8'))
        HTTPServer(('0.0.0.0', int(os.getenv('PORT'))), Binder).serve_forever()
    threading.Thread(target=heroku_binder).start()

log('Started.')
client.run_until_disconnected()
