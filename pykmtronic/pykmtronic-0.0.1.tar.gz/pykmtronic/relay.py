from pykmtronic.auth import Auth
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Relay:
    def __init__(self, number: int, status: bool, auth: Auth):
        self._relay = number
        self.auth = auth
        self.is_on = status  # True means ON

    @property
    def id(self) -> int:
        return self._relay

    @property
    def is_on(self):
        return self._is_on

    @is_on.setter
    def is_on(self, b):
        logger.debug(f"Relay{self._relay} if now {'ON' if b else 'OFF'}")
        self._is_on = b

    async def turn_on(self):
        logger.debug(f"Sending ... FF{self._relay:02}01")
        resp = await self.auth.request(f"FF{self._relay:02}01")
        resp.raise_for_status()
        self.is_on = True

    async def turn_off(self):
        logger.debug(f"Sending ... FF{self._relay:02}00")
        resp = await self.auth.request(f"FF{self._relay:02}00")
        resp.raise_for_status()
        self.is_on = False
