from pymongo.errors import PyMongoError, ConnectionFailure, OperationFailure

from easyqueue.core.response import ResponseCode, ResponseDTO
from easyqueue.utils.validation import TypeValidator


class MongoExceptionMapper:

    MAP_DEFAULT = ResponseCode.UNEXPECTED_ERROR
    MAP = {
        ConnectionFailure: ResponseCode.CONNECTION_ERROR,
        OperationFailure: ResponseCode.OPERATION_ERROR
    }

    @classmethod
    def response_code(cls, exception: PyMongoError) -> ResponseCode:
        TypeValidator.raise_validation_element_type(
            element_name='exception', element=exception, type_class=PyMongoError, allow_none=False)
        response_code = cls.MAP.get(type(exception), cls.MAP_DEFAULT)
        if response_code == cls.MAP_DEFAULT:
            for parent_class in exception.__class__.__bases__:
                response_code = cls.MAP.get(parent_class, cls.MAP_DEFAULT)
                if response_code != cls.MAP_DEFAULT:
                    break
        return response_code

    @classmethod
    def generate_error_response(cls, exception: Exception) -> ResponseDTO:
        return ResponseDTO(code=cls.response_code(exception), msg=str(exception))
