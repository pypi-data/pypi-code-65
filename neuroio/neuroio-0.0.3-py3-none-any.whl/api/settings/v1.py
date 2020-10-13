from httpx import Response

from neuroio.api.base import APIBase, APIBaseAsync
from neuroio.constants import (
    DEFAULT_EXACT_THRESHOLD,
    DEFAULT_HA_THRESHOLD,
    DEFAULT_JUNK_THRESHOLD,
)
from neuroio.utils import request_dict_processing


class Settings(APIBase):
    def get(self) -> Response:
        try:
            return self.client.get(url="/v1/settings/thresholds/")
        finally:
            self.client.close()

    def update(
        self,
        exact: float = DEFAULT_EXACT_THRESHOLD,
        ha: float = DEFAULT_HA_THRESHOLD,
        junk: float = DEFAULT_JUNK_THRESHOLD,
    ) -> Response:
        data = request_dict_processing(locals(), ["self"])

        try:
            return self.client.patch(url="/v1/settings/thresholds/", data=data)
        finally:
            self.client.close()

    def reset(self) -> Response:
        try:
            return self.client.post(url="/v1/settings/thresholds/reset/")
        finally:
            self.client.close()


class SettingsAsync(APIBaseAsync):
    async def get(self) -> Response:
        try:
            return await self.client.get(url="/v1/settings/thresholds/")
        finally:
            await self.client.aclose()

    async def update(
        self,
        exact: float = DEFAULT_EXACT_THRESHOLD,
        ha: float = DEFAULT_HA_THRESHOLD,
        junk: float = DEFAULT_JUNK_THRESHOLD,
    ) -> Response:
        data = request_dict_processing(locals(), ["self"])

        try:
            return await self.client.patch(
                url="/v1/settings/thresholds/", data=data
            )
        finally:
            await self.client.aclose()

    async def reset(self) -> Response:
        try:
            return await self.client.post(url="/v1/settings/thresholds/reset/")
        finally:
            await self.client.aclose()
