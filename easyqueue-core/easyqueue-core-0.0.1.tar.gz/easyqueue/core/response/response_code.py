from enum import Enum


class ResponseCode(Enum):
    UNEXPECTED_ERROR = 0
    OK = 1
    PARTIAL_RESPONSE = 2
    CONNECTION_ERROR = 3
    INVALID_REQUEST = 4
    OPERATION_ERROR = 5
    AUTHENTICATION_ERROR = 6
    NO_CONTENT = 7
