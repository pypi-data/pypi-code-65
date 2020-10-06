from typing import Callable

from fancy.descriptor.method_descriptor_factories import MethodDescriptorFactoryBase
from fancy.descriptor.method_descriptor_base import MethodDescriptorBase, SimpleMethodDescriptor


class SimpleMethodDescriptorFactory(MethodDescriptorFactoryBase):
    def create(self, method: Callable) -> MethodDescriptorBase:
        return SimpleMethodDescriptor(method)


class MethodDescriptorFactories:
    simple = SimpleMethodDescriptorFactory()
