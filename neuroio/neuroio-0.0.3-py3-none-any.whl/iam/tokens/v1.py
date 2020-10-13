from typing import Union

from httpx import Response

from neuroio.api.base import APIBase, APIBaseAsync


class Tokens(APIBase):
    def create(self, permanent: bool = False) -> Response:
        data = {"permanent": permanent}
        try:
            return self.client.post(url="/v1/tokens/", json=data)
        finally:
            self.client.close()

    def list(
        self, permanent: bool = None, limit: int = 20, offset: int = 0
    ) -> Response:
        data = {"permanent": permanent, "limit": limit, "offset": offset}
        try:
            return self.client.get(url="/v1/tokens/", params=data)
        finally:
            self.client.close()

    def get(self, token_id_or_key: Union[int, str]) -> Response:
        try:
            return self.client.get(url=f"/v1/tokens/{token_id_or_key}/")
        finally:
            self.client.close()

    def update(
        self, token_id_or_key: Union[int, str], is_active: bool
    ) -> Response:
        try:
            return self.client.patch(
                url=f"/v1/tokens/{token_id_or_key}/",
                data={"is_active": is_active},
            )
        finally:
            self.client.close()

    def delete_list(self, permanent: bool = None) -> Response:
        data = {"permanent": permanent} if permanent is not None else None
        try:
            return self.client.delete(url="/v1/tokens/", params=data)
        finally:
            self.client.close()

    def delete(self, token_id_or_key: Union[int, str]) -> Response:
        try:
            return self.client.delete(url=f"/v1/tokens/{token_id_or_key}/")
        finally:
            self.client.close()


class TokensAsync(APIBaseAsync):
    async def create(self, permanent: bool = False) -> Response:
        data = {"permanent": permanent}
        try:
            return await self.client.post(url="/v1/tokens/", json=data)
        finally:
            await self.client.aclose()

    async def list(
        self, permanent: bool = None, limit: int = 20, offset: int = 0
    ) -> Response:
        data = {"permanent": permanent, "limit": limit, "offset": offset}
        try:
            return await self.client.get(url="/v1/tokens/", params=data)
        finally:
            await self.client.aclose()

    async def get(self, token_id_or_key: Union[int, str]) -> Response:
        try:
            return await self.client.get(url=f"/v1/tokens/{token_id_or_key}/")
        finally:
            await self.client.aclose()

    async def update(
        self, token_id_or_key: Union[int, str], is_active: bool
    ) -> Response:
        try:
            return await self.client.patch(
                url=f"/v1/tokens/{token_id_or_key}/",
                data={"is_active": is_active},
            )
        finally:
            await self.client.aclose()

    async def delete_list(self, permanent: bool = None) -> Response:
        data = {"permanent": permanent} if permanent is not None else None
        try:
            return await self.client.delete(url="/v1/tokens/", params=data)
        finally:
            await self.client.aclose()

    async def delete(self, token_id_or_key: Union[int, str]) -> Response:
        try:
            return await self.client.delete(
                url=f"/v1/tokens/{token_id_or_key}/"
            )
        finally:
            await self.client.aclose()
