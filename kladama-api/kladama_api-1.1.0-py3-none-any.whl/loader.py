import abc
import json
import re

from enum import Enum
from .entities import *


class ResultType(Enum):
    OK = 0
    REDIRECTION = 1
    ERROR = 2


class ApiResponse(ABC):

    def __init__(self, code: int):
        self._code = code

    @property
    @abc.abstractmethod
    def is_success(self) -> bool:
        pass

    @property
    def code(self) -> int:
        return self._code

    @property
    def type(self) -> ResultType:

        if 200 <= self.code < 300:
            return ResultType.OK

        if 300 <= self.code < 400:
            return ResultType.REDIRECTION

        return ResultType.ERROR


class Error(ApiResponse):

    def __init__(self, code: int, message: str):
        ApiResponse.__init__(self, code)
        self._message = message

    @property
    def is_success(self):
        return False

    @property
    def message(self) -> str:
        return self._message

    def __str__(self):
        return 'Error {0}: {1}'.format(self.code, self.message)


class Success(ApiResponse):

    def __init__(self, code: int, result):
        ApiResponse.__init__(self, code)
        self._result = result

    @property
    def is_success(self):
        return True

    @property
    def result(self):
        return self._result

    def __str__(self):
        return 'Success {0}: {1}'.format(self.code, self._result)


class ResponseLoader:

    @staticmethod
    def load_get_response(response, entities_expected) -> ApiResponse:
        if ResponseLoader._is_success_response(response):

            if ResponseLoader._is_empty_response(response):
                return Success(response.status_code, None)

            if ResponseLoader._is_json(response):
                return Success(response.status_code, ResponseLoader._load_json(response, entities_expected))

            if ResponseLoader._is_binary(response):
                return Success(response.status_code, ResponseLoader._load_binary_result(response))

            return Error(0, 'Unrecognized http response')

        return ResponseLoader._get_error(response)

    @staticmethod
    def load_operation_response(response) -> ApiResponse:
        if ResponseLoader._is_success_response(response):
            content = ResponseLoader._get_content_as_string(response)

            if ResponseLoader._is_json(response):
                return Success(response.status_code, json.loads(content))

            return Success(response.status_code, content)

        return ResponseLoader._get_error(response)

    # private members

    @staticmethod
    def _load_binary_result(response):
        filename_match = re.match('.* filename=(.*)', response.headers['Content-disposition'], re.M | re.I)
        return BinaryResult({
            'name': filename_match.group(1),
            'content': response.content
        })

    @staticmethod
    def _load_json(response, entities_expected):
        obj = json.loads(response.content.decode('utf-8'))

        embedded_key = '_embedded'
        if embedded_key in obj:
            json_obj = obj[embedded_key]
            entities = ResponseLoader._try_load_entities(json_obj)
            if entities is not None:
                return entities

            # if is not an entity just return the json obj
            return json_obj

        if entities_expected:
            # if embedded was expected, return empty list
            return []

        # if embedded is not expected, just return the obj
        return obj

    @staticmethod
    def _try_load_entities(json_obj):
        entities = {
            'areas_of_interest': AreaOfInterest,
            'dates': Date,
            'organizations': Organization,
            'phenomena': Phenomena,
            'triggers': Schedule,
            'sources': Source,
            'operations': SpatialOperation,
            'subscriptions': Subscription,
            'users': User,
            'variables': Variable,
        }

        for entity_name, entity_class in entities.items():
            if entity_name in json_obj:
                result = []
                for entity_obj in json_obj[entity_name]:
                    result.append(entity_class(entity_obj))

                return result

        return None

    @staticmethod
    def _get_content_as_string(response):
        return response.content.decode('utf-8')

    @staticmethod
    def _is_success_response(response):
        return 200 <= response.status_code < 400

    @staticmethod
    def _is_json(response):
        return 'Content-Type' in response.headers and response.headers['Content-Type'] == 'application/json'

    @staticmethod
    def _is_binary(response):
        return 'Content-Type' in response.headers and response.headers['Content-Type'] == 'application/octet-stream'

    @staticmethod
    def _is_empty_response(response):
        return response.status_code == 204

    @staticmethod
    def _get_error(response):
        return Error(response.status_code, ResponseLoader._get_content_as_string(response))
