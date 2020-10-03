import attr

from isilon.api.base import BaseAPI


@attr.s(frozen=True)
class Objects(BaseAPI):
    async def get(self, container_name, object_name, headers: dict = {}, **kwargs):
        """Get object content and metadata."""
        response = await self.base_request(
            self.http.get,
            f"{self.url}/{self.API_VERSION}/AUTH_{self.credentials.account}/{container_name}/{object_name}",
            headers=headers,
            **kwargs,
        )
        return response

    async def get_large(
        self,
        container_name,
        object_name,
        filename,
        chunk_size=50,
        headers: dict = {},
        **kwargs,
    ):
        """Get large object content and metadata."""
        response = await self.base_request(
            self.http.get_large_object,
            f"{self.url}/{self.API_VERSION}/AUTH_{self.credentials.account}/{container_name}/{object_name}",
            filename=filename,
            chunk_size=chunk_size,
            headers=headers,
            **kwargs,
        )
        return response

    async def create(
        self, container_name, object_name, data, headers: dict = {}, **kwargs
    ):
        """Create or replace object."""
        if "Content-Length" not in headers:
            headers.update({"Content-Length": f"{len(data)}"})
        response = await self.base_request(
            self.http.put,
            f"{self.url}/{self.API_VERSION}/AUTH_{self.credentials.account}/{container_name}/{object_name}",
            headers=headers,
            data=data,
            **kwargs,
        )
        return response.status

    async def create_large(
        self, container_name, object_name, filename, headers: dict = {}, *args, **kwargs
    ):
        """Create or replace large object."""
        response = await self.base_request(
            self.http.send_large_object,
            f"{self.url}/{self.API_VERSION}/AUTH_{self.credentials.account}/{container_name}/{object_name}",
            filename=filename,
            headers=headers,
            **kwargs,
        )
        return response.status

    async def copy(self, container_name, object_name, headers: dict = {}, **kwargs):
        """Copy object."""
        raise NotImplementedError("Operation not supported")

    async def delete(self, container_name, object_name, headers: dict = {}, **kwargs):
        """Delete object."""
        response = await self.base_request(
            self.http.delete,
            f"{self.url}/{self.API_VERSION}/AUTH_{self.credentials.account}/{container_name}/{object_name}",
            headers=headers,
            **kwargs,
        )
        return response.status

    async def show_metadata(
        self, container_name, object_name, headers: dict = {}, **kwargs
    ):
        """Show object metadata."""
        response = await self.base_request(
            self.http.head,
            f"{self.url}/{self.API_VERSION}/AUTH_{self.credentials.account}/{container_name}/{object_name}",
            headers=headers,
            **kwargs,
        )
        return response.headers

    async def update_metadata(
        self, container_name, object_name, headers: dict = {}, **kwargs
    ):
        """Create or update object metadata."""
        response = await self.base_request(
            self.http.post,
            f"{self.url}/{self.API_VERSION}/AUTH_{self.credentials.account}/{container_name}/{object_name}",
            headers=headers,
            **kwargs,
        )
        return response.status
