import aiohttp

from aiojson.exception import ApiException


class ApiClient:

    def __init__(self, server_ip, server_port, https=True):
        self.server_ip = server_ip
        self.server_port = server_port
        self.protocol = "https" if https else "http"

    @staticmethod
    def _delete_none(request: dict):
        """Removes None values from request."""

        return {key: value for key, value in request.items() if value is not None}

    def _format_path(self, endpoint):
        return f"{self.protocol}://{self.server_ip}:{self.server_port}/{endpoint}"

    async def _make_request(self, endpoint, method, json_data=None, keep_none=False, headers=None):
        url = self._format_path(endpoint)
        data = self._delete_none(json_data or {}) if not keep_none else json_data or {}
        async with aiohttp.ClientSession() as session:
            _method = getattr(session, method)
            async with _method(url, json=data, headers=headers) as response:
                result = await response.json()
                if result["error"]:
                    raise ApiException(result["reason"].get("text", result["reason"]))
                else:
                    return result["result"]

    async def get(self, endpoint, json_data=None, keep_none=False):
        return await self._make_request(endpoint, "get", json_data=json_data,
                                        keep_none=keep_none)

    async def post(self, endpoint, json_data=None, keep_none=False):
        return await self._make_request(endpoint, "post", json_data=json_data,
                                        keep_none=keep_none)

    async def delete(self, endpoint, json_data=None, keep_none=False):
        return await self._make_request(endpoint, "delete", json_data=json_data,
                                        keep_none=keep_none)

    async def put(self, endpoint, json_data=None, keep_none=False):
        return await self._make_request(endpoint, "put", json_data=json_data,
                                        keep_none=keep_none)

    async def patch(self, endpoint, json_data=None, keep_none=False):
        return await self._make_request(endpoint, "patch", json_data=json_data,
                                        keep_none=keep_none)
