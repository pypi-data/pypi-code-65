from abc import ABC, abstractmethod
from typing import Callable

from fancy.descriptor.method_descriptor_base import MethodDescriptorBase
from fancy.descriptor.patterns import Singleton


class MethodDescriptorFactoryBase(ABC, Singleton):

    @abstractmethod
    def create(self, method: Callable) -> MethodDescriptorBase:
        pass
