from enum import Enum


class DataType(Enum):
    """An enumeration of the allowed data types."""

    token = 'token'
    integer = 'integer'
    floating_point = 'float'

    def __str__(self):
        return self.value
