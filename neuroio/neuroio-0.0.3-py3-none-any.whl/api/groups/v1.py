from typing import List, Union

from httpx import Response

from neuroio.api.base import APIBase, APIBaseAsync
from neuroio.constants import sentinel
from neuroio.utils import request_query_processing


class Groups(APIBase):
    def create(self, name: str) -> Response:
        data = {"name": name}
        try:
            return self.client.post(url="/v1/groups/persons/", json=data)
        finally:
            self.client.close()

    def list(
        self,
        q: Union[str, object] = sentinel,
        pids_include: Union[List[str], object] = sentinel,
        pids_exclude: Union[List[str], object] = sentinel,
        groups_ids: Union[List[int], object] = sentinel,
        spaces_ids: Union[List[int], object] = sentinel,
        limit: int = 20,
        offset: int = 0,
    ) -> Response:
        data = request_query_processing(locals(), ["self"])
        try:
            return self.client.get(url="/v1/groups/persons/", params=data)
        finally:
            self.client.close()

    def get(self, id: int) -> Response:
        try:
            return self.client.get(url=f"/v1/groups/persons/{id}/")
        finally:
            self.client.close()

    def update(self, id: int, name: str) -> Response:
        data = {"name": name}
        try:
            return self.client.patch(
                url=f"/v1/groups/persons/{id}/", json=data
            )
        finally:
            self.client.close()

    def delete(self, id: int) -> Response:
        try:
            return self.client.delete(url=f"/v1/groups/persons/{id}/")
        finally:
            self.client.close()

    def persons(
        self,
        id: int,
        pids: Union[List[str], object] = sentinel,
        limit: int = 20,
        offset: int = 0,
    ) -> Response:
        data = request_query_processing(locals(), ["self", "id"])

        try:
            return self.client.get(
                url=f"/v1/groups/persons/{id}/pids/", params=data
            )
        finally:
            self.client.close()

    def add(self, pids: List[str], groups_ids: List[int]) -> Response:
        data = {"pids": pids, "groups_ids": groups_ids}
        try:
            return self.client.post(url="/v1/groups/persons/pids/", json=data)
        finally:
            self.client.close()

    def remove(self, pids: List[str], groups_ids: List[int]) -> Response:
        data = {"pids": pids, "groups_ids": groups_ids}
        try:
            return self.client.request(
                "DELETE", url="/v1/groups/persons/pids/", json=data
            )
        finally:
            self.client.close()


class GroupsAsync(APIBaseAsync):
    async def create(self, name: str) -> Response:
        data = {"name": name}
        try:
            return await self.client.post(url="/v1/groups/persons/", json=data)
        finally:
            await self.client.aclose()

    async def list(
        self,
        q: Union[str, object] = sentinel,
        pids_include: Union[List[str], object] = sentinel,
        pids_exclude: Union[List[str], object] = sentinel,
        groups_ids: Union[List[int], object] = sentinel,
        spaces_ids: Union[List[int], object] = sentinel,
        limit: int = 20,
        offset: int = 0,
    ) -> Response:
        data = request_query_processing(locals(), ["self"])
        try:
            return await self.client.get(
                url="/v1/groups/persons/", params=data
            )
        finally:
            await self.client.aclose()

    async def get(self, id: int) -> Response:
        try:
            return await self.client.get(url=f"/v1/groups/persons/{id}/")
        finally:
            await self.client.aclose()

    async def update(self, id: int, name: str) -> Response:
        data = {"name": name}
        try:
            return await self.client.patch(
                url=f"/v1/groups/persons/{id}/", json=data
            )
        finally:
            await self.client.aclose()

    async def delete(self, id: int) -> Response:
        try:
            return await self.client.delete(url=f"/v1/groups/persons/{id}/")
        finally:
            await self.client.aclose()

    async def persons(
        self,
        id: int,
        pids: Union[List[str], object] = sentinel,
        limit: int = 20,
        offset: int = 0,
    ) -> Response:
        data = request_query_processing(locals(), ["self", "id"])
        try:
            return await self.client.get(
                url=f"/v1/groups/persons/{id}/pids/", params=data
            )
        finally:
            await self.client.aclose()

    async def add(self, pids: List[str], groups_ids: List[int]) -> Response:
        data = {"pids": pids, "groups_ids": groups_ids}
        try:
            return await self.client.post(
                url="/v1/groups/persons/pids/", json=data
            )
        finally:
            await self.client.aclose()

    async def remove(self, pids: List[str], groups_ids: List[int]) -> Response:
        data = {"pids": pids, "groups_ids": groups_ids}
        try:
            return await self.client.request(
                "DELETE", url="/v1/groups/persons/pids/", json=data
            )
        finally:
            await self.client.aclose()
