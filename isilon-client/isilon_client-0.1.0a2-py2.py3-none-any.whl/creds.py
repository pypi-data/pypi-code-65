import attr

from isilon.exceptions import TokenRetrieveException
from isilon.http import Http


@attr.s(frozen=True)
class Credentials:
    http = attr.ib(type=Http, validator=attr.validators.instance_of(Http), repr=False)
    account = attr.ib(
        type=str, validator=attr.validators.instance_of(str), converter=str
    )
    user = attr.ib(type=str, validator=attr.validators.instance_of(str), converter=str)
    password = attr.ib(
        type=str, validator=attr.validators.instance_of(str), converter=str, repr=False
    )

    async def token(self, url: str, headers: dict = {}):
        headers.update({"X-Storage-User": f"{self.account}:{self.user}"})
        headers.update({"X-Storage-Pass": f"{self.password}"})
        try:
            response = await self.http.get(f"{url}/auth/v1.0", headers=headers)
            return response.headers["X-Auth-Token"]
        except Exception:
            raise TokenRetrieveException

    async def x_auth_token(self, url: str, headers: dict = {}):
        token = await self.token(url, headers)
        return {"X-Auth-Token": token}
