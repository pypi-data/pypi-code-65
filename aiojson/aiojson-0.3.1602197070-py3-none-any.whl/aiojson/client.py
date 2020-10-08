import aiohttp

from aiojson.exception import ApiException


class ApiClient:
    error_field_name = "error"
    error_text_field = "reason"
    result_wrapped_in_field = "result"

    def __init__(self, server_ip, server_port=None, https=True):
        self.server_ip = server_ip
        self.server_port = server_port
        self.protocol = "https" if https else "http"

    @staticmethod
    def _delete_none(request: dict):
        """Removes None values from request."""

        return {key: value for key, value in request.items() if value is not None}

    def _format_path(self, endpoint):
        url = f"{self.protocol}://{self.server_ip}"
        if self.server_port:
            url += f":{self.server_port}"
        url += f"/{endpoint}"
        return url

    async def _make_request(self, endpoint, method, json_data=None, keep_none=False, headers=None):
        url = self._format_path(endpoint)
        data = self._delete_none(json_data or {}) if not keep_none else json_data or {}
        async with aiohttp.ClientSession() as session:
            _method = getattr(session, method)
            async with _method(url, json=data, headers=headers) as response:
                result = await response.json()
                if result.get(self.error_field_name):
                    raise ApiException(result.get(self.error_text_field))
                else:
                    if self.result_wrapped_in_field:
                        return result[self.result_wrapped_in_field]
                    return result

    async def get(self, endpoint, json_data=None, keep_none=False, headers=None):
        return await self._make_request(endpoint, "get", json_data=json_data,
                                        keep_none=keep_none, headers=headers)

    async def post(self, endpoint, json_data=None, keep_none=False, headers=None):
        return await self._make_request(endpoint, "post", json_data=json_data,
                                        keep_none=keep_none, headers=headers)

    async def delete(self, endpoint, json_data=None, keep_none=False, headers=None):
        return await self._make_request(endpoint, "delete", json_data=json_data,
                                        keep_none=keep_none, headers=headers)

    async def put(self, endpoint, json_data=None, keep_none=False, headers=None):
        return await self._make_request(endpoint, "put", json_data=json_data,
                                        keep_none=keep_none, headers=headers)

    async def patch(self, endpoint, json_data=None, keep_none=False, headers=None):
        return await self._make_request(endpoint, "patch", json_data=json_data,
                                        keep_none=keep_none, headers=headers)
