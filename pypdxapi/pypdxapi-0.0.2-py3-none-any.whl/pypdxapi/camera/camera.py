""" Python implementation of Paradox HD7X cameras."""
import logging
import requests
from datetime import datetime
from typing import Optional, Any
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

    def api_request(self, method: str, endpoint: str, payload: Optional[dict] = None,
                    result_code: Optional[int] = None, **kwargs) -> Any:
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

        return self._parse_response(response, result_code)

    def _parse_response(self, response: requests.Response, result_code: Optional[int] = None) -> Any:
        """
        Parse response from requests and check if ResultCode from api is valid.

        :param response: (required) requests.Response.
        :param result_code: (optional) Successful return code to check response.
        :return: JSON data if content type is application/json.
        """
        content_type = response.headers.get('Content-type')
        if content_type != 'application/json':
            return response.content

        data = response.json()
        _LOGGER.debug(f"Result: {data}")

        if result_code is None:
            return data
        else:
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

    def _close_session(self) -> None:
        """Close open client session."""
        if self._session and self._can_close_session:
            self._session.close()

    def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        self._close_session()
