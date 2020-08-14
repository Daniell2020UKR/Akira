import aiohttp, asyncio

xdl_file_too_big = "XDL_FILE_TOO_BIG"
xdl_download_error = "XDL_DOWNLOAD_ERROR"
xdl_parse_error = "XDL_PARSE_ERROR"
xdl_api_error = "XDL_API_ERROR"
xdl_invalid_url = "XDL_INVALID_URL"
xdl_unknown_error = "XDL_UNKNOWN_ERROR"
xdl_aria2 = "XDL_ARIA2"
xdl_path = "XDL_PATH"
xdl_ytdl = "XDL_YTDL"

async def xdl_animekisa(client, url, output_dir, callback, maxsize=2048):
	async with aiohttp.ClientSession() as session:
		try:
			async with session.get(url) as site:
				fembed_id = None
				async for line in site.content:
					line = line.decode("UTF-8")
					if "var Fembed" in line and "var Fembed2" not in line:
						fembed_id = line.split("\"")[1].split("/")[-1]
		except:
			return xdl_parse_error

		if fembed_id:
			try:
				async with session.post(f"https://fcdn.stream/api/source/{fembed_id}") as api:
					videos = (await api.json())["data"]
			except:
				return xdl_api_error

			index = -1
			while True:
				try:
					download = client.add_uris([videos[index]["file"]], options={"dir": output_dir})
				except:
					return xdl_api_error
				percent = int(download.progress)
				eta = download.eta_string()
				size = download.total_length_string()
				speed = download.download_speed_string()
				while not download.is_complete and not download.has_failed:
					download.update()
					if (download.total_length / 1048576) > maxsize:
						index -= 1
						if len(videos) + (index + 1) == 0:
							download.remove(files=True)
							return xdl_file_too_big
						download.remove(files=True)
						try:
							download = client.add_uris([videos[index]["file"]], options={"dir": output_dir})
						except:
							return xdl_api_error
						continue
					if percent != int(download.progress):
						percent = int(download.progress)
						eta = download.eta_string()
						size = download.total_length_string()
						speed = download.download_speed_string()
					await callback(percent, eta, size, speed)
					await asyncio.sleep(1)
				download.update()
				if download.has_failed:
					download.remove(files=True)
					return xdl_download_error
				return [xdl_aria2, download]
		else:
			return xdl_parse_error

async def xdl_url(client, url, output_dir, callback, maxsize=2048):
	try:
		download = client.add_uris([url], options={"dir": output_dir})
	except:
		return xdl_invalid_url
	percent = int(download.progress)
	eta = download.eta_string()
	size = download.total_length_string()
	speed = download.download_speed_string()
	while not download.is_complete and not download.has_failed:
		download.update()
		if (download.total_length / 1048576) > maxsize:
			download.remove(files=True)
			return xdl_file_too_big
		if percent != int(download.progress):
			percent = int(download.progress)
			eta = download.eta_string()
			size = download.total_length_string()
			speed = download.download_speed_string()
		await callback(percent, eta, size, speed)
		await asyncio.sleep(1)
	download.update()
	if download.has_failed:
		download.remove(files=True)
		return xdl_download_error
	return [xdl_aria2, download]

downloaders = {
	"animekisa": xdl_animekisa,
	"url": xdl_url
}
