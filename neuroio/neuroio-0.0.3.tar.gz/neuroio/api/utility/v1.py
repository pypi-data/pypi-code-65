from typing.io import BinaryIO

from httpx import Response

from neuroio.api.base import APIBase, APIBaseAsync
from neuroio.constants import EntryResult


class Utility(APIBase):
    def compare(
        self, image1: BinaryIO, image2: BinaryIO, result: str = EntryResult.HA
    ) -> Response:
        files = {"image1": image1, "image2": image2}
        data = {"result": result}
        try:
            return self.client.post(
                url="/v1/utility/compare/", data=data, files=files
            )
        finally:
            self.client.close()

    def asm(self, image: BinaryIO) -> Response:
        files = {"image": image}
        try:
            return self.client.post(url="/v1/utility/asm/", files=files)
        finally:
            self.client.close()


class UtilityAsync(APIBaseAsync):
    async def compare(
        self, image1: BinaryIO, image2: BinaryIO, result: str = EntryResult.HA
    ) -> Response:
        files = {"image1": image1, "image2": image2}
        data = {"result": result}
        try:
            return await self.client.post(
                url="/v1/utility/compare/", data=data, files=files
            )
        finally:
            await self.client.aclose()

    async def asm(self, image: BinaryIO) -> Response:
        files = {"image": image}
        try:
            return await self.client.post(url="/v1/utility/asm/", files=files)
        finally:
            await self.client.aclose()
