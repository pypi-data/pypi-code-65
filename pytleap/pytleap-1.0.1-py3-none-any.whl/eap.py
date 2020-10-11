"""Represents the EAP device."""
import hashlib

from aiohttp import ClientError, ClientSession, CookieJar

from .client import Client
from .error import AuthenticationError, PytleapError, RequestError, convert_exception
from .utils import normalize_mac


class Eap:
    """ Model of an EAP device"""

    def __init__(self, url: str, username: str, password: str, ssl: bool = True):
        self.url = url
        self.username = username
        self.password = password
        self.ssl = ssl

        self.session = None
        self.is_connected = False

        self._data = {}

    @property
    def mac_address(self) -> str:
        """Return the MAC address of the EAP."""
        return normalize_mac(self._data.get("mac"))

    @property
    def name(self) -> str:
        """Return the name of the EAP."""
        return self._data.get("deviceName")

    async def connect(self):
        """Connect to the EAP device."""
        if self.is_connected:
            return

        # By default, forbids cookie from URLs with IP address instead of DNS name
        jar = CookieJar(unsafe=True)
        # Need referer to be accepted
        self.session = ClientSession(cookie_jar=jar, headers={"Referer": self.url})

        hashed_password = hashlib.md5(self.password.encode("utf-8"))
        try:
            await self.session.get(self.url)
            await self.session.post(
                self.url,
                data={
                    "username": self.username,
                    "password": hashed_password.hexdigest().upper(),
                },
            )
            # Retrieve device info on login
            await self._async_retrieve_device_info()
        except ClientError as err:
            await self.disconnect()
            raise convert_exception("Could not login on EAP device", err) from err
        self.is_connected = True

    async def disconnect(self):
        """Close the connection to the EAP device."""
        if self.session is None:
            return

        try:
            await self.session.get(f"{self.url}/logout.html")
        except ClientError:
            # Ignore error, as we are logging out anyway
            pass
        finally:
            await self.session.close()
            self.is_connected = False
            self.session = None

    async def get_wifi_clients(self) -> [Client]:
        """Retrieve the list of connected Wifi clients."""
        if not self.is_connected:
            await self.connect()

        try:
            resp = await self._async_make_query_json(
                "data/status.client.user.json", "load"
            )
        except ClientError as err:
            await self.disconnect()
            raise convert_exception(
                "Could not retrieve client list from EAP device", err
            ) from err

        return [Client(c) for c in resp]

    async def _async_retrieve_device_info(self):
        self._data = await self._async_make_query_json(
            "data/status.device.json", "read"
        )

    async def _async_make_query_json(self, path: str, operation: str) -> dict:
        """Make a GET query to a given path that returns JSON"""
        async with self.session.get(f"{self.url}/{path}?operation={operation}") as resp:
            resp_j = await resp.json(content_type="text/html")
            if resp_j is None or not resp_j["success"] or resp_j["timeout"] != "false":
                try:
                    await self.disconnect()
                except PytleapError:
                    pass  # Ignore exception here as we are trying our best
                if resp_j is not None and resp_j["timeout"]:
                    raise AuthenticationError("Authentication invalid or expired")
                raise RequestError(
                    f"Cannot query device for {path}, with operation {operation}. "
                    f"Received: '{resp_j}'"
                )
            return resp_j["data"]
