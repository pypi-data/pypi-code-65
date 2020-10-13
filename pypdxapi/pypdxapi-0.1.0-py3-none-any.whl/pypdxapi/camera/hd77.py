""" Python implementation of Paradox HD77 camera."""
import logging
from typing import Any, List
from datetime import datetime

from .camera import ParadoxCamera

_LOGGER = logging.getLogger(__name__)


class ParadoxHD77(ParadoxCamera):
    """

    """

    def __init__(self, host: str, port: int, module_password: str, **kwargs) -> None:
        """ Constructs a :class:`ParadoxHD77 <ParadoxHD77>`.

        :param host: (required) The IP address of your Paradox camera.
        :param port: (required) The port of your Paradox camera.
        :param module_password: (required) The module password. The default value is usually
            paradox.
        :param client_session: (optional) aiohttp.ClientSession for performing HTTP requests.
             If not provided, a new one will be created and later destroyed.
        :param request_timeout: (optional) Request timeout. Default is 10sec.
        :param user_agent: (optional) HTTP user agent. Default is "PyPdxApi/" + Package_Version.
        :param raise_on_response_error: (optional) Raise exception on response error.
            Default is false.
        """
        super().__init__(host=host, port=port, module_password=module_password, **kwargs)

    @staticmethod
    def _client_datetime() -> str:
        """ Return current datetime in timestamp """
        return str(datetime.now().timestamp())

    async def login(self, usercode: str, username: str) -> dict:
        """ Logs the user into the camera and obtains the camera data such as: series, version,
        model and name.
        It also stores the session key for access to other functions that require authentication.
        This session key will expire if not used in 2 minutes.

        :param usercode: (required) User code on the panel.
        :param username: (required) User name on the panel.
        :return: JSON data from camera
        """
        payload = {
            "DeviceID": '',
            "ClientDateTime": self._client_datetime(),
            "tslen": 1,
            "CPUserId": 1,
            "UserCode": usercode,
            "DeveloperKey": self._developer_key,
            "ServerPassword": self._module_password,
            "UserName": username
        }
        self._session_key = None

        data = await self.api_request('POST', endpoint='/app/login', payload=payload,
                                      result_code=33554432)

        if isinstance(data, dict):
            if 'ResultCode' in data and data['ResultCode'] == 33554432:
                self._name = data['Server']['Label'].strip()
                self._model = 'HD77'
                self._serial = data['Server']['SerialNo'].strip()
                self._version = data['Server']['SdCardVersion'].strip()
                self._session_key = data['sessionKey']

        return data

    def logout(self) -> None:
        """
        Set session_key to None so you will not be able to make calls that require authentication.

        :return: None
        """
        self._session_key = None

    async def pingstatus(self) -> dict:
        """ Get some info from camera and panel. This not require login.

        :return: JSON data from camera
        """
        payload = {
            "DeveloperKey": self._developer_key,
            "ClientDateTime": self._client_datetime(),
            "ServerPassword": self._module_password,
        }

        return await self.api_request('POST', endpoint='/app/pingstatus', payload=payload,
                                      result_code=35127296)

    async def getstatus(self, status_type: int, keep_alive: bool = False) -> dict:
        """ Get more info from camera and panel like zones, areas, status, etc...

        :param status_type: (required) It can be 1, 2, or 3. Each one returns a type of information.
        :param keep_alive: (optional) I still don't know what it's for.
        :return: JSON data from camera
        """
        payload = {
            "ClientDateTime": self._client_datetime(),
            "StatusType": status_type,
            "SessionKey": self._session_key,
            "keepAlive": keep_alive
        }

        return await self.api_request('POST', endpoint='/app/getstatus', payload=payload,
                                      result_code=33619968)

    async def rod(self, action: int = 3, rec_resolution: int = 720) -> dict:
        """ Command recording on demand (ROD).

        :param action: (optional) 3 -> Start recording
        :param rec_resolution: (optional) Recording resolution
        :return: JSON data from camera
        """
        payload = {
            "ClientDateTime": self._client_datetime(),
            "Action": action,
            "SessionKey": self._session_key,
            "RecResolution": rec_resolution
        }

        return await self.api_request('POST', endpoint='/app/rod', payload=payload,
                                      result_code=33816578)

    async def areacontrol(self, area_commands: List[dict]) -> dict:
        """ Send arming and disarming commands to the panel.

        :param area_commands: (required) Array of dict
            [{"ForceZones": False, "AreaCommand": 6, "AreaID": 1}]:
            "ForceZones": True|False
            "AreaCommand": One of:
                4 -> Arm Away,
                6 -> Disarm,
            "AreaID": Number of area on panel.
        :return: JSON data from camera
        """
        payload = {
            "AreaCommands": area_commands,
            "ClientDateTime": self._client_datetime(),
            "SessionKey": self._session_key
        }

        return await self.api_request('POST', endpoint='/app/areacontrol', payload=payload)

    async def getitemlist(self, items_count: int = 150, direction: str = 'Ascending',
                          order_by: str = 'date', item_index: int = 0) -> dict:
        """ Returns the list of files stored on the camera

        :param items_count: (optional) Max number of items to be returned. Default is 150
        :param direction: (optional) Sorting direction. Default is Ascending
        :param order_by: (optional) Order by. Default is date
        :param item_index: (optional) Start index. Default is 0
        :return: JSON data from camera
        """
        payload = {
            "ClientDateTime": self._client_datetime(),
            "ItemsCount": items_count,
            "Direction": direction,
            "OrderBy": order_by,
            "SessionKey": self._session_key,
            "ItemIndex": item_index
        }

        return await self.api_request('POST', endpoint='/fil/getitemlist', payload=payload,
                                      result_code=33882112)

    async def deleteitem(self, item_id: str) -> dict:
        """ Delete recording file

        :param item_id: (required) File id returned in getitemlist
        :return: JSON data from camera
        """
        payload = {
            "ItemId": item_id,
            "ClientDateTime": self._client_datetime(),
            "SessionKey": self._session_key,
        }

        return await self.api_request('POST', endpoint='/fil/deleteitem', payload=payload,
                                      result_code=34144256)

    async def playback(self, item_id: str, action: int = 0) -> dict:
        """ Prepares the recording file to play and returns the url for access.

        :param item_id: (required) File id returned in getitemlist
        :param action: (optional) I still don't know what it's for.
        :return: JSON data from camera
        """
        payload = {
            "ClientDateTime": self._client_datetime(),
            "Action": action,
            "SessionKey": self._session_key,
            "ItemId": item_id
        }

        return await self.api_request('POST', endpoint='/fil/playback', payload=payload,
                                      result_code=544210944)

    async def getthumbnail(self) -> Any:
        """ Capture a thumbnail in real time.

        :return: JPEG Image
        """
        payload = {
            "ClientDateTime": self._client_datetime(),
            "SessionKey": self._session_key
        }

        return await self.api_request('POST', endpoint='/fil/getthumbnail', payload=payload,
                                      result_code=0)

    async def vod(self, action: int = 1, channel_type: str = 'normal') -> Any:
        """ Request the video on demand and return an m3u8 file containing the access urls.

        :param action: (optional) 1 for start VOD, 2 for stop and invalidate session. Default is 1
        :param channel_type: (optional) Video quality.
        :return: m3u8 file.
        """
        payload = {
            "ClientDateTime": self._client_datetime(),
            "Action": action,
            "SessionKey": self._session_key,
            "ChannelType": channel_type,
        }

        return await self.api_request('POST', endpoint='/hls/vod', payload=payload, result_code=0)
