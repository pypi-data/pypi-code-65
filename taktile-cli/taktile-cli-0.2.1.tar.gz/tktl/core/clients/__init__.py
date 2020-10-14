from abc import ABC, abstractmethod

from tktl.core.clients.taktile import TaktileClient
from tktl.core.config import settings
from tktl.core.t import ServiceT
from tktl.login import login


class Client(ABC):

    TRANSPORT: str = ServiceT

    def __init__(self, api_key: str):
        login(api_key)
        self.taktile_client = TaktileClient(api_url=settings.DEPLOYMENT_API_URL)

    @abstractmethod
    def predict(self, *args, **kwargs):
        ...

    @abstractmethod
    def list_endpoints(self):
        ...

    @abstractmethod
    def list_deployments(self):
        ...

    @abstractmethod
    def get_sample_data(self):
        ...

    @abstractmethod
    def get_schema(self, *args, **kwargs):
        ...
