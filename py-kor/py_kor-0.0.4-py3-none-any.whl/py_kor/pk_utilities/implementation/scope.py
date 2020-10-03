from typing import Callable, Any, Type
from types import TracebackType
from .utilities.function_helpers import empty_call


class Scope:
    """
    Scope actions
    """
    def __init__(self,
                 on_enter: Callable[[], None] = empty_call,
                 on_exit: Callable[[], None] = empty_call):
        self.__on_enter = on_enter
        self.__on_exit = on_exit

    def __enter__(self):
        self.__on_enter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__on_exit()


class EScope(Scope):
    """
    Scope actions with internal error handler
    """
    def __init__(self,
                 on_enter: Callable[[], None] = empty_call,
                 on_exit: Callable[[], None] = empty_call,
                 on_exception: Callable[[Type[Exception], Exception, Any], bool] = empty_call):
        super(EScope, self).__init__(self, on_enter=on_enter, on_exit=on_exit)
        self.__on_exception = on_exception

    def __exit__(self, ex_type: Type[Exception], ex_value: Exception, ex_traceback: TracebackType):
        self.__on_exception(ex_type, ex_value, ex_traceback)
        self.__on_exit()
