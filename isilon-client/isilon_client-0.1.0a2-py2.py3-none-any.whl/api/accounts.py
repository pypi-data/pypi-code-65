import attr

from isilon.api.base import BaseAPI


@attr.s(frozen=True)
class Accounts(BaseAPI):
    async def show(self, account_name, headers: dict = {}, **kwargs):
        """Show account details and list containers."""
        response = await self.base_request(
            self.http.get,
            f"{self.url}/{self.API_VERSION}/{account_name}?format=json",
            headers=headers,
            **kwargs,
        )
        response = await response.json()
        return response

    async def update(self, account_name, headers: dict = {}, **kwargs):
        """Create, update, or delete account metadata."""
        response = await self.base_request(
            self.http.post,
            f"{self.url}/{self.API_VERSION}/{account_name}",
            headers=headers,
            **kwargs,
        )
        return response

    async def metadata(self, account_name, headers: dict = {}, **kwargs):
        """Show account metadata."""
        response = await self.base_request(
            self.http.head,
            f"{self.url}/{self.API_VERSION}/{account_name}",
            headers=headers,
            **kwargs,
        )
        return response.headers
