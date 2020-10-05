from enum import Enum


class RestHeaders(Enum):
    ACCEPT_STR = "Accept"
    ACCEPT_ALL = "*/*"
    APP_JSON = "application/json"
    CONT_TYPE = "Content-type"
    AUTHORIZATION = "Authorization"
