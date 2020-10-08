import abc
from ..constants.enums import HttpCode
from .contract import LoggingInterface


class Response:
    """Response object for use cases.

    Attributes:
        _http_code (constants.enums.HttpCode):
            Guarantee valid code. Default HttpCode.OK.
        message (str): A message.
        errors (list): List of errors.

    Examples:
        Instantiate class.

        >>> r = Response(http_code=200, message='OK')
        >>> r.message
        'OK'
    """

    def __init__(
        self,
        http_code: int = None,
        message: str = None,
        errors: list = None
    ):
        # Default HttpCode
        self._http_code: HttpCode = HttpCode.OK

        self.http_code = http_code
        self.message = message
        self.errors = errors

    @property
    def http_code(self) -> int:
        """int: code http"""
        if self._http_code:
            return self._http_code.value
        return None

    @http_code.setter
    def http_code(self, http_code) -> None:
        """validate http code"""
        if isinstance(http_code, HttpCode):
            self._http_code = http_code
        elif http_code:
            self._http_code = HttpCode(http_code)

    def __json__(self):
        return {
            'http_code': self.http_code,
            'message': self.message,
            'errors': self.errors,
        }


class UseCaseInterface(metaclass=abc.ABCMeta):
    """Contract for use cases.

    Attributes:
        _path (str): A path.
        _logger (utils.contract.LoggingInterface): Logger class.
    """
    _path = None
    _logger: LoggingInterface = None

    def _debugger(self, message):
        """Run if the debug is actived.

        Args:
            message (str): A message.
        """
        self._logger.debug(
            '{}: {}'.format(self._path, message)
            )

    def _error(self, message):
        """Error log.

        Args:
            message (str): A message.
        """
        self._logger.error(
            '{}: {}'.format(self._path, message)
            )

    @abc.abstractmethod
    def handle(self, *args, **kwargs) -> Response:
        """Unique public methed, return use case result.

        Args:
            request (dict): (Optional) Recommended.
            args: Other positional arguments.
            kwargs: Other keyword arguments.

        Returns:
            Response: Response Instance or
                daughter class (recommended if you want to
                return data other than attributes of the reponse).
        """
        pass


class ExportResponse(Response):
    """Response for use cases export file.

    Attributes:
        _http_code (constants.enums.HttpCode):
            Guarantee valid code. Default HttpCode.OK.
        message (str): A message.
        errors (list): List of errors.
        file_name (str): A filename or path.

    Examples:
        Instantiate class.

        >>> r = Response(http_code=200, message='OK', file_name='file.csv')
        >>> r.file_name
        'file.csv'
    """
    def __init__(self, file_name: str = None, *args, **kwargs):
        self.file_name = file_name

        super().__init__(*args, **kwargs)

    def __json__(self):
        result = super().__json__()
        result['file_name'] = self.file_name
        return result


class DataResponse(Response):
    """Response object for use cases.

    Attributes:
        http_code (constants.enums.HttpCode):
            Guarantee valid code. Default HttpCode.OK.
        message (str): A message.
        errors (list): List of errors.
        data (dict): body.

    Examples:
        Instantiate class.

        >>> r = Response(http_code=200, message='OK', data={})
        >>> r.message
        'OK'
        >>> r.data
        {}
    """

    def __init__(
        self,
        data: dict = None,
        *args,
        **kwargs
    ):
        self.data = data
        super().__init__(*args, **kwargs)

    def __json__(self):
        return {
            'http_code': self.http_code,
            'message': self.message,
            'errors': self.errors,
            'data': self.data,
        }
