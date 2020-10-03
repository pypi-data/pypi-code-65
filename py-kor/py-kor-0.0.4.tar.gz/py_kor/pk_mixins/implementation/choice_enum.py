from enum import Enum
from .generics import T
from typing import List, Tuple, Generic


class ChoiceEnum(Enum):
    """
    Extension for python enum. It can be used as mixin for choices in Django field choices
    """
    @classmethod
    def choices(cls) -> Tuple[Tuple[Generic[T], str]]:
        return tuple((item.value, item.name) for item in cls)

    @classmethod
    def values(cls) -> List[Generic[T]]:
        """
        Get list of available items in enum
        """
        return [item.value for item in cls]

    @classmethod
    def names(cls) -> List[str]:
        """
        Get list of available names in enum
        """
        return [item.name for item in cls]
