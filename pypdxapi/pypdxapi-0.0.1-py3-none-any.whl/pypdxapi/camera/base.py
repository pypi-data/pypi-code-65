""" Python implementation of Paradox HD7X cameras."""
import logging
from datetime import datetime
from typing import Optional
import requests
from yarl import URL

from pypdxapi.version import __version__
from pypdxapi.base import ParadoxModule
from pypdxapi.camera.exceptions import ParadoxCameraError

_LOGGER = logging.getLogger(__name__)


class ParadoxCamera(ParadoxModule):
    """

    """
    _developer_key: str = 'client'
    _session_key: Optional[str] = None
    _last_api_call: Optional[datetime] = None
    _can_close_session: bool = False

    def __init__(self, host: str, port: int, module_password: str,
                 session: requests.Session = None,
                 request_timeout: Optional[int] = None,
                 user_agent: Optional[str] = None,
                 raise_on_response_error: bool = False) -> None:

        self._session = session
        self._request_timeout: int = request_timeout if request_timeout else 10
        self._user_agent: str = user_agent if user_agent else f"PyPdxApi/{__version__}"
        self._raise_on_response_error: bool = raise_on_response_error

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

    @staticmethod
    def _client_datetime() -> str:
        """ Return current datetime in timestamp """
        return str(datetime.now().timestamp())

    def _api_request(self, method: str, endpoint: str, payload: Optional[dict] = None,
                     **kwargs) -> requests.Response:
        """ Handle a request to camera. """
        headers = {
            "User-Agent": self._user_agent,
            "Content-Type": "application/json",
        }
        url = str(self._url.with_path(endpoint))
        if 'timeout' not in kwargs:
            kwargs.update({'timeout': self._request_timeout})

        if self._session is None:
            self._session = requests.Session()
            self._can_close_session = True

        _LOGGER.debug(f"{method} to {url} with payload: {payload}")
        response = self._session.request(method, url, headers=headers, json=payload, **kwargs)
        response.raise_for_status()
        self._last_api_call = datetime.now()

        return response

    def _raise_for_response_error(self, data: Optional[dict] = None) -> None:
        """ Raise error"""
        if self._raise_on_response_error:
            if data and 'ResultCode' in data:
                msg = f"Error no {data['ResultCode']}: {data['ResultStr']}"
            else:
                msg = 'Unknown error occurred while communicating with Paradox camera.'

            raise ParadoxCameraError(msg)

    def _close_session(self) -> None:
        """Close open client session."""
        if self._session and self._can_close_session:
            self._session.close()

    def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        self._close_session()
