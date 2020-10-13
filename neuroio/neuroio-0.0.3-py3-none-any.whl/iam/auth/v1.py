from httpx import Response

from neuroio.api.base import APIBase, APIBaseAsync


class Auth(APIBase):
    def login(self, username: str, password: str) -> Response:
        data = {"username": username, "password": password}
        try:
            return self.client.post(url="/v1/login/", json=data)
        finally:
            self.client.close()

    def password_change(
        self, old_password: str, new_password: str, reset_tokens: bool = False
    ) -> Response:
        data = {
            "old_password": old_password,
            "password": new_password,
            "password2": new_password,
            "reset_tokens": reset_tokens,
        }
        try:
            return self.client.post(url="/v1/auth/password/change/", json=data)
        finally:
            self.client.close()


class AuthAsync(APIBaseAsync):
    async def login(self, username: str, password: str) -> Response:
        data = {"username": username, "password": password}
        try:
            return await self.client.post(url="/v1/login/", json=data)
        finally:
            await self.client.aclose()

    async def password_change(
        self, old_password: str, new_password: str, reset_tokens: bool = False
    ) -> Response:
        data = {
            "old_password": old_password,
            "password": new_password,
            "password2": new_password,
            "reset_tokens": reset_tokens,
        }
        try:
            return await self.client.post(
                url="/v1/auth/password/change/", json=data
            )
        finally:
            await self.client.aclose()
