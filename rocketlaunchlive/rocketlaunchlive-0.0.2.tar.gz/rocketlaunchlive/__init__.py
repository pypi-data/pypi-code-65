"""Simple PyPi Wrapper for the Rocket Launch Live Next 5 Launches API."""

import logging
import aiohttp
import json

_LOGGER = logging.getLogger("rocketlaunchlive")

BASE_URL = "https://fdo.rocketlaunch.live/json/launches/next/5"

class RocketLaunchLive:
    def __init__(
        self, 
        session:aiohttp.ClientSession=None,
        key:str=None,
    ):
        """Initialize the session."""
        self.retry = 5
        if not session:
            self._session = aiohttp.ClientSession()
        else:
            self._session = session       

        if key != "":
            self._key = key
        else:
            self._key = None

    async def close(self):
        """Close the session."""
        await self._session.close()

    async def get_next_launches(self):
        """Get the next launch data from rocketlaunch.live."""
        response = {}

        if self._key:
            request_url = f"{BASE_URL}?key={self._key}"
        else:
            request_url = BASE_URL

        async with await self._session.get(request_url) as resp:
            response = await resp.text()

        if response is not None:
            try:
                return json.loads(response)
            except json.decoder.JSONDecodeError as error:
                raise ValueError(f"Error decoding data from rocketlaunch.live ({error}).")
            except Exception as error:
                raise ValueError(f"Unknown error in rocketlaunch.live data ({error})")
        else:
            raise ConnectionError("Error getting data from rocketlaunch.live.")
