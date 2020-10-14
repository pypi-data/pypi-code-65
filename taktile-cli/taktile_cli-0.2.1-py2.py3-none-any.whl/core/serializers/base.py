import abc
from abc import ABC
from typing import Any

import pyarrow
from pydantic import BaseModel


class ObjectSerializer(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def serialize(cls, value: Any) -> pyarrow.Table:
        raise NotImplemented

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, value: Any) -> Any:
        raise NotImplemented


class CustomDeserializingModelT(ABC, BaseModel):
    def deserialize(self):
        ...
