import abc

import httpx


class APIBase(abc.ABC):
    def __init__(self, client: httpx.Client) -> None:
        self.client = client


class APIBaseAsync(abc.ABC):
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
