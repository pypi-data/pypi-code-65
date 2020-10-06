from copy import copy
from typing import Callable

from fancy.descriptor.method_descriptor_base import MethodDescriptorBase


class SimpleMethodDescriptor(MethodDescriptorBase):
    """
    This class provide a simplest implementation of MethodDescriptorBase
    Any class should not mark methods as this descriptor, except in testing.
    See MethodDescriptor
    """

    def __init__(self, method: Callable):
        if not isinstance(method, Callable):
            raise TypeError('method must be a Callable.')
        self.method = method
        self.instance = None
        self.owner = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            raise RuntimeError('method must bind to an instance first.')
        return self._get_method_of_instance()(*args, **kwargs)

    def _get_method_of_instance(self):
        return self.method.__get__(self.instance, self.owner)

    def __get__(self, instance, owner=None):
        new_instance = self.clone()
        new_instance.instance = instance
        new_instance.owner = owner

        return new_instance

    def clone(self):
        return copy(self)

    def get_method(self) -> Callable:
        return self.method
