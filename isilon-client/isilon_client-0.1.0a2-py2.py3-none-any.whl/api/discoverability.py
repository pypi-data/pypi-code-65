import attr

from isilon.api.base import BaseAPI


@attr.s(frozen=True)
class Discoverability(BaseAPI):
    async def info(self, *args, **kwargs):
        """List activated capabilities."""
        response = await self.base_request(
            self.http.get, f"{self.url}/info", *args, **kwargs
        )
        json_response = await response.json()
        return json_response
