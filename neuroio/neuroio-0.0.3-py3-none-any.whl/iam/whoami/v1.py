from httpx import Response

from neuroio.api.base import APIBase, APIBaseAsync


class Whoami(APIBase):
    def me(self) -> Response:
        try:
            return self.client.get(url="/v1/whoami/")
        finally:
            self.client.close()


class WhoamiAsync(APIBaseAsync):
    async def me(self) -> Response:
        try:
            return await self.client.get(url="/v1/whoami/")
        finally:
            await self.client.aclose()
