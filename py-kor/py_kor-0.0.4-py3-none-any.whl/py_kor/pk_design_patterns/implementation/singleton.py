from typing import Any


class Singleton(type):
    """
    Pattern Singleton metaclass
    """
    __instance = None

    def __call__(cls, *args, **kwargs) -> Any:
        if cls.__instance is None:
            cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.__instance
