from typing import Any
from easyqueue.core.response import ResponseCode
from easyqueue.utils.validation import TypeValidator


class ResponseDTO:

    def __init__(self, code: ResponseCode, msg: str = '', data: Any = None):
        TypeValidator.raise_validation_element_type(
            element_name='code', element=code, type_class=ResponseCode, allow_none=False)
        TypeValidator.raise_validation_element_type(element_name='msg', element=msg, type_class=str, allow_none=True)

        self.__code = code
        self.__msg = msg
        self.__data = data

    @property
    def code(self):
        return self.__code

    @property
    def msg(self):
        return self.__msg

    @property
    def data(self):
        return self.__data

    def __eq__(self, other):
        return self.code == other.code and self.msg == other.msg and self.data == other.data

    def __str__(self):
        return 'RepositoryResponse(code={code}[{n_code}], msg="{msg}", data_type="{d_type}")'.format(
            code=self.code, n_code=self.code.value, msg=self.msg, d_type=self.__data.__class__.__name__)
