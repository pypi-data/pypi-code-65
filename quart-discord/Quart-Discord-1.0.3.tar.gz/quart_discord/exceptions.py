import json


class HttpException(Exception):
    """Base Exception class representing a HTTP exception."""


class RateLimited(HttpException):
    """A HTTP Exception raised when the application is being rate limited.
    It provides the ``response`` attribute which can be used to get more details of the actual response from
    the Discord API with few more shorthands to ``response.json()``.

    Attributes
    ----------
    resp_as_json : dict
        The actual JSON data received. Value yielded from ``response.json()`` coroutine.
    message : str
        A message saying you are being rate limited.
    retry_after : int
        The number of milliseconds to wait before submitting another request.
    is_global : bool
        A value indicating if you are being globally rate limited or not
    """

    def __init__(self, resp_as_json, message, is_global, retry_after):
        self.resp_as_json = resp_as_json
        self.message = message
        self.is_global = is_global
        self.retry_after = retry_after
        super().__init__(self.message)

    @classmethod
    async def create(cls, response):
        """Coroutine to convert an aiohttp response into a RateLimited exception.
        
        Attributes
        ----------
        response : aiohttp.Response
            the aiohttp Response object.
            
        """
        try:
            resp_as_json = await response.json()
        except json.JSONDecodeError:
            resp_as_json = dict()
            message = await response.text()
        else:
            message = resp_as_json["message"]
            is_global = resp_as_json["global"]
            retry_after = resp_as_json["retry_after"]
        return RateLimited(resp_as_json, message, is_global, retry_after)


class Unauthorized(HttpException):
    """A HTTP Exception raised when user is not authorized."""


class AccessDenied(HttpException):
    """Exception raised when user cancels OAuth authorization grant."""
