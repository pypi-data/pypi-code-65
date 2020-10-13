from datetime import datetime
from typing import List, Union

from httpx import Response

from neuroio.api.base import APIBase, APIBaseAsync
from neuroio.constants import EntryLiveness, EntryMood, EntryResult, sentinel
from neuroio.utils import request_query_processing


class Entries(APIBase):
    def list(
        self,
        pid: Union[List[str], object] = sentinel,
        result: Union[List[EntryResult], object] = sentinel,
        age_from: Union[int, object] = sentinel,
        age_to: Union[int, object] = sentinel,
        sex: Union[int, object] = sentinel,
        mood: Union[List[EntryMood], object] = sentinel,
        liveness: Union[List[EntryLiveness], object] = sentinel,
        sources_ids: Union[List[int], object] = sentinel,
        spaces_ids: Union[List[int], object] = sentinel,
        date_from: Union[datetime, object] = sentinel,
        date_to: Union[datetime, object] = sentinel,
        limit: int = 20,
        offset: int = 0,
    ) -> Response:
        data = request_query_processing(locals(), ["self"])
        try:
            return self.client.get(url="/v1/entries/", params=data)
        finally:
            self.client.close()

    def get(self, pid: str) -> Response:
        try:
            return self.client.get(url=f"/v1/entries/stats/pid/{pid}/")
        finally:
            self.client.close()

    def delete(self, pid: str) -> Response:
        try:
            return self.client.delete(url=f"/v1/entries/{pid}/")
        finally:
            self.client.close()


class EntriesAsync(APIBaseAsync):
    async def list(
        self,
        pid: Union[List[str], object] = sentinel,
        result: Union[List[EntryResult], object] = sentinel,
        age_from: Union[int, object] = sentinel,
        age_to: Union[int, object] = sentinel,
        sex: Union[int, object] = sentinel,
        mood: Union[List[EntryMood], object] = sentinel,
        liveness: Union[List[EntryLiveness], object] = sentinel,
        sources_ids: Union[List[int], object] = sentinel,
        spaces_ids: Union[List[int], object] = sentinel,
        date_from: Union[datetime, object] = sentinel,
        date_to: Union[datetime, object] = sentinel,
        limit: int = 20,
        offset: int = 0,
    ) -> Response:
        data = request_query_processing(locals(), ["self"])
        try:
            return await self.client.get(url="/v1/entries/", params=data)
        finally:
            await self.client.aclose()

    async def get(self, pid: str) -> Response:
        try:
            return await self.client.get(url=f"/v1/entries/stats/pid/{pid}/")
        finally:
            await self.client.aclose()

    async def delete(self, pid: str) -> Response:
        try:
            return await self.client.delete(url=f"/v1/entries/{pid}/")
        finally:
            await self.client.aclose()
