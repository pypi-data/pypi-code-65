from typing import Callable
from unittest.mock import MagicMock

from fancy.descriptor import MethodDescriptor
from fancy.descriptor.method_descriptor_factories import MethodDescriptorFactoryBase


class FakeMethodDescriptorFactory(MethodDescriptorFactoryBase, MagicMock):
    def create(self, method: Callable) -> MethodDescriptor:
        pass
