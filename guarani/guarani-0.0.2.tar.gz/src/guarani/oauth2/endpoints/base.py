from guarani.oauth2.adapter import BaseAdapter
from guarani.oauth2.client_authentication import ClientAuthentication
from guarani.oauth2.configuration import Configuration
from guarani.oauth2.models import OAuth2Request, OAuth2Response


class BaseEndpoint:
    """
    Base class for the endpoints of the OAuth 2.1 framework and its extensions.

    Any endpoint being implemented by the application or by extensions **MUST**
    inherit from this class and implement its abstract methods.

    The type, status, headers and body of the response it returns,
    as well as its meaning and formatting have to be documented
    by the respective endpoint.

    The method :meth:`create_response` **MUST NOT** raise exceptions.
    It **MUST** catch the exceptions and return a valid error response instead.

    :cvar ``__endpoint__``: Name of the endpoint.

    :param request: Current request being processed.
    :type request: OAuth2Request

    :param adapter: Adapter registered within the Provider.
    :type adapter: BaseAdapter

    :param config: Configuration data of the Provider.
    :type config: Configuration

    :param client_auth: Client Authentication object to authenticate the current Client.
    :type client_auth: ClientAuthentication
    """

    __endpoint__: str = None

    def __init__(
        self,
        request: OAuth2Request,
        adapter: BaseAdapter,
        config: Configuration,
        client_auth: ClientAuthentication,
    ) -> None:
        self.request = request
        self.adapter = adapter
        self.config = config
        self.client_auth = client_auth

    async def __call__(self) -> OAuth2Response:
        """
        Makes the endpoint callable for the Provider.

        :return: Response of the endpoint.
        :rtype: OAuth2Response
        """

        raise NotImplementedError

    async def validate_request(self) -> None:
        """
        Method used to validate the incoming request.
        **ALL** endpoints **MUST** implement this method.
        """

        raise NotImplementedError

    async def create_response(self) -> OAuth2Response:
        """
        Method used to create the response of the Endpoint back to the Client.
        **ALL** endpoints **MUST** implement this method.

        :return: Response containing all the necessary info to the client.
        :rtype: OAuth2Response
        """

        raise NotImplementedError
