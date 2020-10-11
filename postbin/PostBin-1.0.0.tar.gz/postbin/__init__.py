import typing

try:
    import requests
    RR = requests.Response
except ImportError:
    requests = None
    RR = None

try:
    import aiohttp
    CR = aiohttp.ClientResponse
except ImportError:
    aiohttp = None
    CR = None


class ResponseError(Exception):
    """Generic class raised when contacting the server failed."""
    def __init__(self, response: typing.Union[RR,CR]):
        self.raw_response = response
        self.status = getattr(response, "status", response.status_code)


# noinspection PyIncorrectDocstring
def postSync(content: str, *, url: str = None):
    """
    Creates a new haste

    :param content:
    :keyword url: the custom URL to post to. Defaults to HasteBin.
    :return: the returned URL
    """
    if not requests:
        raise RuntimeError("requests must be installed if you want to be able to run postSync.")
    url = url or "https://hastebin.com"
    with requests.Session() as session:
        response = session.post(url+"/documents", data=content)
        if response.status_code != 200:
            raise ResponseError(response)
        key = response.json()["key"]
    return url+"/"+key

async def postAsync(content: str, *, url: str = None):
    """The same as :func:postSync, but async."""
    if not aiohttp:
        raise RuntimeError("aiohttp must be installed if you want to be able to run postAsync.")
    url = url or "https://hastebin.com"
    async with aiohttp.ClientSession() as session:
        async with session.post(url+"/documents", data=content) as response:
            if response.status != 200:
                raise ResponseError(response)
            key = (await response.json())["key"]
    return url+"/"+key
