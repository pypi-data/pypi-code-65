import attr

from isilon.api.base import BaseAPI


@attr.s(frozen=True)
class Containers(BaseAPI):
    async def objects(self, container_name: str, headers: dict = {}, **kwargs):
        """Show container details and list objects."""
        response = await self.base_request(
            self.http.get,
            f"{self.url}/{self.API_VERSION}/AUTH_{self.credentials.account}/{container_name}?format=json",
            headers=headers,
            **kwargs,
        )
        response = await response.json()
        return response

    async def create(self, container_name, headers: dict = {}, **kwargs) -> int:
        """Create container."""
        response = await self.base_request(
            self.http.put,
            f"{self.url}/{self.API_VERSION}/AUTH_{self.credentials.account}/{container_name}",
            headers=headers,
            **kwargs,
        )
        return int(response.status)

    async def update_metadata(self, container_name, headers: dict = {}, **kwargs):
        """Create, update, or delete container metadata."""
        response = await self.base_request(
            self.http.put,
            f"{self.url}/{self.API_VERSION}/AUTH_{self.credentials.account}/{container_name}",
            headers=headers,
            **kwargs,
        )
        return response.status

    async def show_metadata(self, container_name, headers: dict = {}, **kwargs):
        """Show container metadata."""
        response = await self.base_request(
            self.http.head,
            f"{self.url}/{self.API_VERSION}/AUTH_{self.credentials.account}/{container_name}",
            headers=headers,
            **kwargs,
        )
        return response.headers

    async def delete(self, container_name, headers: dict = {}, **kwargs):
        """Delete container."""
        response = await self.base_request(
            self.http.delete,
            f"{self.url}/{self.API_VERSION}/AUTH_{self.credentials.account}/{container_name}",
            headers=headers,
            **kwargs,
        )
        return response.status
