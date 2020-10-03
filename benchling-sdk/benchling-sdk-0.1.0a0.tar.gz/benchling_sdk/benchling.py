import re
from typing import Optional
import urllib.parse

from benchling_api_client.benchling_client import BenchlingApiClient
from benchling_api_client.client import Client

from benchling_sdk.helpers.retry_helpers import RetryStrategy
from benchling_sdk.services.assay_run_service import AssayRunService
from benchling_sdk.services.container_service import ContainerService
from benchling_sdk.services.custom_entity_service import CustomEntityService
from benchling_sdk.services.folder_service import FolderService
from benchling_sdk.services.plate_service import PlateService
from benchling_sdk.services.registry_service import RegistryService
from benchling_sdk.services.request_service import RequestService
from benchling_sdk.services.task_service import TaskService


class Benchling(object):

    _client: Client
    _container_service: ContainerService
    _registry_service: RegistryService
    _task_service: TaskService
    _custom_entity_service: CustomEntityService
    _request_service: RequestService
    _assay_run_service: AssayRunService
    _plate_service: PlateService
    _folder_service: FolderService

    def __init__(
        self,
        url: str,
        api_key: str,
        base_path: Optional[str] = "/api/v2",
        retry_strategy: Optional[RetryStrategy] = RetryStrategy(),
    ):
        """
        :param url: A server URL (host and optional port) including scheme such as https://benchling.com
        :param api_key: A valid Benchling API token for authentication and authorization
        :param base_path: If provided, will append to the host. Otherwise, assumes the V2 API. This is
                          a workaround until the generated client supports the servers block. See BNCH-15422
        :param retry_strategy: An optional retry strategy for retrying HTTP calls on failure. Setting to None
                               will disable retries
        """
        full_url = self._format_url(url, base_path)
        client = BenchlingApiClient(base_url=full_url, token=api_key)
        if retry_strategy is None:
            retry_strategy = RetryStrategy.no_retries()
        self._client = client
        self._container_service = ContainerService(client, retry_strategy=retry_strategy)
        self._registry_service = RegistryService(client, retry_strategy=retry_strategy)
        self._task_service = TaskService(client, retry_strategy=retry_strategy)
        self._custom_entity_service = CustomEntityService(
            client,
            retry_strategy=retry_strategy,
            registry_service=self._registry_service,
            task_service=self._task_service,
        )
        self._request_service = RequestService(client, retry_strategy=retry_strategy)
        self._assay_run_service = AssayRunService(client, retry_strategy=retry_strategy)
        self._plate_service = PlateService(client, retry_strategy=retry_strategy)
        self._folder_service = FolderService(client, retry_strategy=retry_strategy)

    @property
    def client(self) -> Client:
        return self._client

    @property
    def assay_runs(self) -> AssayRunService:
        return self._assay_run_service

    @property
    def containers(self) -> ContainerService:
        return self._container_service

    @property
    def custom_entities(self) -> CustomEntityService:
        return self._custom_entity_service

    @property
    def folders(self) -> FolderService:
        return self._folder_service

    @property
    def plates(self) -> PlateService:
        return self._plate_service

    @property
    def registry(self) -> RegistryService:
        return self._registry_service

    @property
    def requests(self) -> RequestService:
        return self._request_service

    @property
    def tasks(self) -> TaskService:
        return self._task_service

    @staticmethod
    def _format_url(url: str, base_path: Optional[str]) -> str:
        if base_path:
            joined_url = urllib.parse.urljoin(url, base_path)
            # Strip any trailing slashes, the API client will lead with them
            joined_url = re.sub(r"/+$", "", joined_url)
            return joined_url
        return url
