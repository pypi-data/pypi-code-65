""" Python implementation of Paradox HD7X cameras."""
import logging
from datetime import datetime, timedelta
from typing import Optional, Any
import async_timeout
import aiohttp
from yarl import URL

from pypdxapi.__version__ import __version__
from pypdxapi.module import ParadoxModule
from pypdxapi.exceptions import ParadoxCameraError

_LOGGER = logging.getLogger(__name__)


class ParadoxCamera(ParadoxModule):
    """

    """
    _developer_key: str = 'client'
    _session_key: Optional[str] = None
    _last_api_call: Optional[datetime] = None
    _can_close_session: bool = False

    # pylint: disable=too-many-arguments
    def __init__(
            self,
            host: str,
            port: int,
            module_password: str,
            client_session: aiohttp.ClientSession = None,
            request_timeout: Optional[int] = None,
            user_agent: Optional[str] = None,
            raise_on_response_error: bool = False) -> None:

        self._client_session = client_session
        self._request_timeout = request_timeout if request_timeout else 10
        self._user_agent = user_agent if user_agent else f"PyPdxApi/{__version__}"
        self._raise_on_response_error = raise_on_response_error

        self._url: URL = URL.build(scheme='http', host=host, port=port)
        super().__init__(host=host, port=port, module_password=module_password)

    @property
    def session_key(self) -> Optional[str]:
        """ Return module name. """
        return self._session_key

    @property
    def last_api_call(self) -> Optional[datetime]:
        """ Return last api call."""
        return self._last_api_call

    def is_authenticated(self, timeout: int = 120) -> bool:
        """ Returns true, session_key is valid and is not expired, otherwise false.

        :param timeout: Time (in seconds) for the session to be considered expired.
        :return: True/False
        """
        if self._session_key is None:
            return False

        if isinstance(self._last_api_call, datetime):
            last = self._last_api_call
            now = datetime.now()

            if now - last < timedelta(seconds=timeout):
                return True

        return False

    async def api_request(self, method: str, endpoint: str, payload: Optional[dict] = None,
                          result_code: Optional[int] = None) -> Any:
        """ Handle an async request to camera. """
        headers = self._get_headers()
        url = self._url.with_path(endpoint)

        if self._client_session is None:
            self._client_session = aiohttp.ClientSession()
            self._can_close_session = True

        _LOGGER.debug("Async %s to %s  with payload: %s", method, url, payload)
        with async_timeout.timeout(self._request_timeout):
            response = await self._client_session.request(
                method,
                url,
                json=payload,
                headers=headers,
                raise_for_status=True
            )
        self._last_api_call = datetime.now()

        if response.content_type != 'application/json':
            return await response.text()

        data = await response.json()
        return self._parse_response(data, result_code)

    def _get_headers(self) -> dict:
        return {
            "User-Agent": self._user_agent,
            "Content-Type": "application/json",
        }

    def _parse_response(self, data: dict, result_code: Optional[int] = None) -> dict:
        """
        Parse response from api request and check if ResultCode is valid.

        :param data: (required) JSON data from api.
        :param result_code: (optional) Successful return code to check response.
        :return: JSON data.
        """
        _LOGGER.debug("Result: %s", data)

        if result_code is None:
            return data

        if 'ResultCode' in data:
            if data['ResultCode'] == result_code:
                return data
        else:
            data = {
                "ResultCode": -1,
                "ResultStr": "Unknown error occurred while communicating with Paradox camera."
            }

        if self._raise_on_response_error:
            raise ParadoxCameraError(f"Error no {data['ResultCode']}: {data['ResultStr']}")

        return data

    async def _async_close_session(self) -> None:
        if self._client_session and self._can_close_session:
            await self._client_session.close()

    # pylint: disable=invalid-name
    async def __aexit__(self, exc_type, exc, tb):
        """Async exit."""
        await self._async_close_session()
