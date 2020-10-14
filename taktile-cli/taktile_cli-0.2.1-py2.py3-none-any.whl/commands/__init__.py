import abc

from tktl.core.clients.http_client import API
from tktl.core.config import settings
from tktl.core.loggers import CliLogger


class CommandBase(object):
    def __init__(self, api=None, logger=CliLogger()):
        self.api = api
        self.logger = logger


class BaseApiCommand:

    __metaclass__ = abc.ABCMeta

    def __init__(
        self, logger=CliLogger(), api_url=settings.DEPLOYMENT_API_URL,
    ):
        self.api_url = api_url
        self.logger = logger
        self.client = self._get_client()

    @abc.abstractmethod
    def execute(self, *args, **kwargs):
        pass

    def _get_client(self):
        return API(api_url=self.api_url, logger=self.logger)


class BaseDeploymentApiCommand(BaseApiCommand):
    def __init__(self):
        super().__init__(api_url=settings.DEPLOYMENT_API_URL)

    def execute(self, *args, **kwargs):
        raise NotImplementedError


class BaseTaktileApiCommand(BaseApiCommand):
    def __init__(self):
        super().__init__(api_url=settings.TAKTILE_API_URL)

    def execute(self, *args, **kwargs):
        raise NotImplementedError
