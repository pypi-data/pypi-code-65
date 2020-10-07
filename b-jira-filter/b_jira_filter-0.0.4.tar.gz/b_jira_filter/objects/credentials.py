import os
from typing import Optional

from jira import JIRA
from jira.resources import GreenHopperResource
from requests.auth import HTTPBasicAuth


class Credentials:
    """
    Credentials class for authentication.
    """
    def __init__(
            self,
            username: Optional[str] = None,
            password: Optional[str] = None,
            server: Optional[str] = None
    ) -> None:
        """
        Constructor.

        :param username: Username for authentication.
        :param password: Password for authentication.
        :param server: Server where your JIRA resources are.
        """
        self.username = username or os.environ.get('JIRA_USERNAME') or input('Username: ')
        self.password = password or os.environ.get('JIRA_PASSWORD') or input('Password: ')
        self.server = server or os.environ.get('JIRA_SERVER') or input('Server: ')

    @property
    def basic_auth(self) -> HTTPBasicAuth:
        """
        Creates basic authorization instance.

        :return: Basic auth instance.
        """
        return HTTPBasicAuth(self.username, self.password)

    @property
    def jira_sdk(self) -> JIRA:
        """
        Creates JIRA SDK instance.

        :return: JIRA SDK instance.
        """
        return JIRA(
            server=self.server,
            basic_auth=(self.username, self.password),
            options={
                'agile_rest_path': GreenHopperResource.AGILE_BASE_REST_PATH
            }
        )
