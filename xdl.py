import aiohttp, urllib, asyncio

xdl_file_too_big = "XDL_FILE_TOO_BIG"
xdl_download_error = "XDL_DOWNLOAD_ERROR"
xdl_parse_error = "XDL_PARSE_ERROR"
xdl_api_error = "XDL_API_ERROR"
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
				with urllib.request.urlopen(videos[index]["file"]) as video:
					video_size = int(video.info()["Content-Length"])
					if (video_size / 1048576) > maxsize:
						index -= 1
						if len(videos) + (index + 1) == 0:
							return xdl_file_too_big
						continue

					download = client.add_uris([videos[index]["file"]], options={"dir": output_dir})
					while not download.is_complete and not download.has_failed:
						download.update()
						await callback(int(download.progress), download.eta_string(), download.total_length_string(), download.download_speed_string())
						await asyncio.sleep(1)
					download.update()
					return [xdl_aria2, download]
		else:
			return xdl_parse_error

downloaders = {
	"animekisa": xdl_animekisa
}
