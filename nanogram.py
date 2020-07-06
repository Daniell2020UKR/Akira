# Nanogram 0.1
# Minimal Telegram Bot API library
# Dependencies: aiohttp, pyOpenSSL
import aiohttp, asyncio, ssl, OpenSSL
from aiohttp import web

class Nanogram:
	def __init__(self, token):
		self.token = token
		self.session = aiohttp.ClientSession()
		self.loop = asyncio.get_event_loop()
		self.commands = {}
		self.me = self.loop.run_until_complete(self.api_request('getMe'))

	def stringizer(self, some_dict):
		for k, v in some_dict.items():
			if type(v) == dict: some_dict[k] = self.stringizer(v)
			if type(v) == int: some_dict[k] = str(v)
		return some_dict

	def generate_ssl_certificate(self, url):
		k = OpenSSL.crypto.PKey()
		k.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)
		cert = OpenSSL.crypto.X509()
		cert.get_subject().C = 'UK'
		cert.get_subject().ST = 'London'
		cert.get_subject().O = 'Nanogram'
		cert.get_subject().CN = url
		cert.set_issuer(cert.get_subject())
		cert.gmtime_adj_notBefore(0)
		cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
		cert.set_pubkey(k)
		cert.sign(k, 'sha256')

		with open('nanogram.crt', 'wb') as f: f.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert))
		with open('nanogram.prv', 'wb') as f: f.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, k))

	async def api_request(self, postfix, **kwargs):
		async with self.session.post(f'https://api.telegram.org/bot{self.token}/{postfix}', data=kwargs.get('postdata')) as response:
			jsondata = await response.json()
			if jsondata.get('ok'): return jsondata.get('result')
			else: raise Exception(jsondata.get('description'))

	async def process_update(self, update):
		update = self.stringizer(update)
		if update.get('message'):
			if update.get('message').get('text'):
				update['message']['args'] = update['message']['text'].split(' ')
				command = update['message']['args'].pop(0).split('@')
				if command[0] in self.commands.keys():
					if len(command) == 2 and self.me.get('username') in command:
						asyncio.create_task(self.commands[command[0]](self, update))
					elif len(command) == 1 and self.me.get('username') not in command:
						asyncio.create_task(self.commands[command[0]](self, update))

	async def send_message(self, text, **kwargs):
		request = {'text': text}
		request.update(kwargs)
		return await self.api_request('sendMessage', postdata=request)

	async def send_photo(self, photo, **kwargs):
		request = {'photo': photo}
		request.update(kwargs)
		return await self.api_request('sendPhoto', postdata=request)

	async def send_audio(self, audio, **kwargs):
		request = {'audio': audio}
		request.update(kwargs)
		return await self.api_request('sendAudio', postdata=request)

	async def send_sticker(self, sticker, **kwargs):
		request = {'sticker': sticker}
		request.update(kwargs)
		return await self.api_request('sendSticker', postdata=request)

	async def edit_message(self, text, **kwargs):
		request = {'text': text}
		request.update(kwargs)
		return await self.api_request('editMessageText', postdata=request)

	def add_command(self, command, function):
		self.commands.update({command: function})

	def set_webhook(self, url, port):
		self.webhook_port = port
		self.generate_ssl_certificate(url)
		async def webhook(request):
			await self.process_update(await request.json())
			return web.Response(text='ACK')
		self.loop.run_until_complete(self.api_request('setWebhook', postdata={'url': f'https://{url}:{port}/{self.token}', 'certificate': open('nanogram.crt', 'rb'), 'max_connections': '100'}))
		self.app = web.Application()
		self.app.router.add_post(f'/{self.token}', webhook)

	def delete_webhook(self):
		self.loop.run_until_complete(self.api_request('deleteWebhook'))

	def start_webhook(self):
		context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
		context.load_cert_chain('nanogram.crt', 'nanogram.prv')
		web.run_app(self.app, port=self.webhook_port, ssl_context=context)
