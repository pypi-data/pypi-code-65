import attr

from isilon.creds import Credentials
from isilon.http import Http


@attr.s(frozen=True)
class BaseAPI:
    API_VERSION = "v1"
    http = attr.ib(type=Http, repr=False)
    url = attr.ib(type=str, validator=attr.validators.instance_of(str), converter=str)
    credentials = attr.ib(
        type=Credentials, validator=attr.validators.instance_of(Credentials)
    )

    async def base_request(self, fn, url, headers: dict = {}, *args, **kwargs):
        headers = await self.get_token(headers)
        response = await fn(url, headers=headers, *args, **kwargs)
        return response

    async def get_token(self, headers: dict) -> dict:
        token = await self.credentials.x_auth_token(self.url)
        headers.update(token)
        return headers
