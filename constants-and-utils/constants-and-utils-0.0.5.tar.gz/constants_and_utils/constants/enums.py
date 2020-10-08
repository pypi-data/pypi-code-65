from enum import Enum, unique


@unique
class HttpCode(Enum):
    """Http code constants.

    Examples:
        Use case.

        >>> HttpCode.OK.value
        200
    """
    # 2xx Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    # 4xx Client Error
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406

    # 5xx Server Error
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    GATEWAY_TIMEOUT = 504

    @staticmethod
    def values() -> list:
        """returns list of values"""
        return list(map(lambda e: e.value, HttpCode))


@unique
class Gender(Enum):
    """Gender constants.

    Examples:
        Use case.

        >>> Gender.FEMALE.value
        'F'
    """
    FEMALE = 'F'
    MALE = 'M'

    @staticmethod
    def values() -> list:
        """returns list of values"""
        return list(map(lambda e: e.value, Gender))
