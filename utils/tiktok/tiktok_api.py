import aiohttp

async def get_response(url, mode=False):
    url = f"https://api.douyin.wtf/api/hybrid/video_data?url={url}&minimal={mode}"
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        async with session.get(url) as response:
            data = await response.json()
    return data["data"]["video"]["play_addr"]["url_list"][0]

