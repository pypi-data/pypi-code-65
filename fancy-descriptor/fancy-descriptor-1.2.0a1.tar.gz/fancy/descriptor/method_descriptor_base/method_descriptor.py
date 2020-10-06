from copy import copy
from typing import Callable

from fancy.descriptor.method_descriptor_base import MethodDescriptorBase
from fancy.descriptor.method_descriptor_factories import MethodDescriptorFactoryBase, SimpleMethodDescriptorFactory


class MethodDescriptor(MethodDescriptorBase):
    """
    The MethodDescriptor is a kind of proxy, it forwarding requests to the true instance of the descriptor.
    All method descriptors classes should inherit this class, except classes which this proxy forwarded.
    """
    true_instance: MethodDescriptorBase

    def __init__(self, method: Callable, factory: MethodDescriptorFactoryBase = None):
        """
        :param method: input method
        :param factory: a factory decides which kind of true instance will be initialized.
        """
        if factory is None:
            # default factory
            factory = SimpleMethodDescriptorFactory()
        self.true_instance = factory.create(method)

    def __call__(self, *args, **kwargs):
        return self.true_instance.__call__(*args, **kwargs)

    def __get__(self, instance, owner):
        new_instance = self.clone()
        new_instance.true_instance = self.true_instance.__get__(instance, owner)
        return new_instance

    def clone(self):
        return copy(self)

    def get_method(self) -> Callable:
        return self.true_instance.get_method()

    @classmethod
    def bind(cls, *args, **kwargs):
        def inner(method: Callable):
            return cls(method, *args, **kwargs)

        return inner
