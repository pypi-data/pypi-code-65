from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus, urlparse

from guarani.webtools import FullDict, json_dumps, to_bytes, to_string, urldecode


class OAuth2Request:
    def __init__(
        self,
        method: str,
        url: str,
        headers: dict[str, Any],
        body: bytes = None,
        user: Any = None,
    ):
        if method.lower() not in ("get", "post"):
            raise RuntimeError(f'The method "{method}" is not supported.')

        self.method = method
        self.url = url
        self.path = urlparse(url).path
        self.query = urldecode(urlparse(url).query)
        self.fragment = urldecode(urlparse(url).fragment)
        self.headers = {k.lower(): v for k, v in headers.items()}
        self.user = user
        self.client = None

        self._body = body

        # Data of the current request.
        self.data = self.query if method.lower() == "get" else self.form()

    def form(self) -> dict:
        return urldecode(to_string(self._body))


class OAuth2Response:
    media_type: str = None

    def __init__(self, status: int = 200, headers: dict = None, body: Any = None):
        self.status = status
        self.headers = self.parse_headers(headers)
        self.body = self.parse_body(body)

    def parse_headers(self, headers: dict) -> dict:
        if headers is None:
            headers = {}

        return FullDict({"Content-Type": self.media_type}, **headers)

    def parse_body(self, body: Any = None) -> bytes:
        return to_bytes(body) or b""


class OAuth2JSONResponse(OAuth2Response):
    media_type: str = "application/json"

    def parse_body(self, body: Any = None) -> bytes:
        return to_bytes(json_dumps(body))


class OAuth2RedirectResponse(OAuth2Response):
    def __init__(self, url: str, status: int = 303, headers: dict = None):
        super().__init__(status=status, headers=headers, body=b"")
        self.headers["Location"] = quote_plus(url, safe=":/%#?&=@[]!$&'()*+,;")
