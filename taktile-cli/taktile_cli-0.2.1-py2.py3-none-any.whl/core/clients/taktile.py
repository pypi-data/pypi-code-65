from typing import List

from .. import loggers as sdk_logger
from ..config import settings
from ..exceptions import TaktileSdkError
from ..managers.auth import AuthConfigManager
from ..schemas.repository import Endpoint, Repository, RepositoryDeployment
from ..utils import flatten, lru_cache
from .http_client import API, interpret_response


class TaktileClient(API):

    SCHEME: str

    def __init__(self, api_url, logger=sdk_logger.MuteLogger()):
        """
        Base class. All client classes inherit from it.
        """
        super().__init__(api_url, logger=logger)
        self.api_url = api_url
        self.api_key = AuthConfigManager.get_api_key()
        self.logger = logger

    @lru_cache(timeout=50, typed=False)
    def _get_repositories(self) -> List[Repository]:
        response = self.get(f"{settings.API_V1_STR}/models")
        return interpret_response(response=response, model=Repository)

    def get_repositories(self):
        repositories = self._get_repositories()
        return repositories

    def get_deployments_for_repository(
        self, repository_name: str, repository_owner: str = None
    ) -> List[RepositoryDeployment]:
        repos = [
            r for r in self.get_repositories() if r.repository_name == repository_name
        ]
        if not repos:
            raise TaktileSdkError(f"No repositories with name {repository_name} found")
        if len(repos) > 1:
            if not repository_owner:
                raise TaktileSdkError(
                    f"More than one repository with name {repository_name} found, please specify repository_owner"
                )
            try:
                return [r for r in repos if r.repository_owner == repository_owner][
                    0
                ].deployments
            except IndexError:
                raise TaktileSdkError(
                    f"No repository named {repository_name} with owner {repository_owner}"
                )
        else:
            return repos[0].deployments

    def get_endpoints_for_deployment(
        self, repository_name: str, repository_owner: str = None
    ) -> List[Endpoint]:
        deployments = self.get_deployments_for_repository(
            repository_name=repository_name, repository_owner=repository_owner
        )
        return list(flatten([r.endpoints for r in deployments]))

    def get_endpoint(
        self, endpoint_name: str, repository_name: str, repository_owner: str = None
    ):
        endpoints = [
            e
            for e in self.get_endpoints_for_deployment(
                repository_name=repository_name, repository_owner=repository_owner
            )
            if e.name == endpoint_name
        ]
        if not endpoints:
            raise TaktileSdkError(
                f"No endpoints named {endpoint_name} found for repository named {repository_name} "
                f"with owner {repository_owner}"
            )
