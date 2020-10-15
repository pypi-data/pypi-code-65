from dataclasses import dataclass, InitVar
from typing import *

from http_server_base.auth import BearerAuthorizationProvider, OAuth2AuthorizationProvider
from ._code_gen.client import RingcentralApiClient, RingcentralApiClientServers as RingCentralApiClientServers

@dataclass
class RingCentralClient(RingcentralApiClient):
    client_id: InitVar[Optional[str]] = None
    client_secret: InitVar[Optional[str]] = None
    redirect_uri: InitVar[Optional[str]] = None
    application_token: InitVar[Optional[str]] = None
    server: Union[str, RingCentralApiClientServers] = RingCentralApiClientServers.SandboxServer.value
    
    def __post_init__(self, client_id: Optional[str], client_secret: Optional[str], redirect_uri: Optional[str], application_token: Optional[str]):
        if (isinstance(self.server, RingCentralApiClientServers)):
            self.server = self.server.value
        
        if (application_token is not None):
            self.auth_provider = BearerAuthorizationProvider(application_token)
        elif (client_id is not None):
            self.provide_o_auth2_authorization()
            self.auth_provider = OAuth2AuthorizationProvider(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, token_url='/restapi/oauth/token', authorization_url='/restapi/oauth/authorize', subrequest_client=self)

__all__ = \
[
    'RingCentralClient',
    'RingCentralApiClientServers',
]
