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

async def xdl_url(client, url, output_dir, maxsize=2048):
	try:
		download = client.add_uris([url], options={"dir": output_dir})
	except:
		return xdl_invalid_url
	while not download.is_complete and not download.has_failed:
		download.update()
		if (download.total_length / 1048576) > maxsize:
			download.remove(files=True)
			return xdl_file_too_big
		await asyncio.sleep(1)
	download.update()
	if download.has_failed:
		download.remove(files=True)
		return xdl_download_error
	return [xdl_aria2, download]

downloaders = {
	"url": xdl_url
}
