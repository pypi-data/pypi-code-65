from guarani.oauth2.authentication.base import BaseClientAuthentication
from guarani.oauth2.exceptions import InvalidClient
from guarani.oauth2.mixins import ClientMixin
from guarani.oauth2.models import OAuth2Request
from guarani.webtools import get_basic_authorization


class ClientSecretBasic(BaseClientAuthentication):
    """
    Implements the Client Authentication via the Basic Authentication workflow.

    If this workflow is enabled, it will look at the Authorization header
    for a scheme similar to the following::

        Basic Y2xpZW50MTpjbGllbnQxc2VjcmV0

    This scheme denotes the type of the flow, which in this case is `Basic`,
    and the Client Credentials, that is a Base64 encoded string that contains
    the Credentials in the format `client_id:client_secret`.
    """

    __method__: str = "client_secret_basic"

    async def authenticate(self, request: OAuth2Request) -> ClientMixin:
        client_id, client_secret = get_basic_authorization(request.headers)

        if not client_id or not client_secret:
            return None

        client = await self.find_client(client_id)
        headers = {"WWW-Authenticate": "Basic"}

        if not client:
            raise InvalidClient("Client not found.", headers=headers)

        if not client.validate_client_secret(client_secret):
            raise InvalidClient("Mismatching Client Secret.", headers=headers)

        if client.get_token_endpoint_auth_method() != self.__method__:
            raise InvalidClient(
                f'This Client is not allowed to use the method "{self.__method__}".',
                headers=headers,
            )

        return client
