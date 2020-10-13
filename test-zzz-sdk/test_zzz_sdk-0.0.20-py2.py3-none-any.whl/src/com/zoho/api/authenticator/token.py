from abc import abstractmethod, ABC


class Token(ABC):

    """
    The class to verify and set token to the APIHTTPConnector instance, to authenticate requests.
    """

    @abstractmethod
    def authenticate(self, url_connection):

        try:
            from zcrmsdk.src.com.zoho.crm.api.util import APIHTTPConnector
        except Exception:
            from ...crm.api.util import APIHTTPConnector

        """
        This method to set token to APIHTTPConnector instance

        Parameters:
            url_connection (APIHTTPConnector) : A APIHTTPConnector class instance.
        """

        pass

    @abstractmethod
    def remove(self):

        """
        The method to remove the token from store.

        Returns:
            bool: A Boolean value representing the removed status.
        """
        pass
