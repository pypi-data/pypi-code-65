import typing

from httpx import Auth, Request, Response


class AuthorizationTokenAuth(Auth):
    """Describes an API Token requests authentication."""

    def __init__(self, api_token: str, header_name: str = None):
        """
        :param api_token: The API token that will be sent.
        :param header_name: Name of the header field.
        """
        self.api_token = api_token
        self.header_name = header_name or "Authorization"

    def auth_flow(
        self, request: Request
    ) -> typing.Generator[Request, Response, None]:
        request.headers[self.header_name] = f"Token {self.api_token}"
        yield request
