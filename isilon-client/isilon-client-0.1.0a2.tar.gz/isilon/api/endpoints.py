import attr

from isilon.api.base import BaseAPI


@attr.s(frozen=True)
class Endpoints(BaseAPI):
    async def __call__(self, headers: dict = {}, **kwargs):
        """List endpoints."""
        response = await self.base_request(
            self.http.get,
            f"{self.url}/{self.API_VERSION}/endpoints",
            headers=headers,
            **kwargs,
        )
        return response.status
