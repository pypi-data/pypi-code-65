#!/usr/bin/env python

## Standard Lib
from collections import OrderedDict
from inspect import Parameter, Signature

## TTILS:
from .terrors import NodeError
from .conf import *
from .validation import Descriptor

__all__ = ['Node']


class MetaNode(type):

    @classmethod
    def __prepare__(cls, name, bases):
        return OrderedDict()

    def __new__(cls, clsname, bases, clsdict):
        if len(bases) > 1:
            raise NodeError(
                "Inheritance hierarchy unclear creating class:", clsname)
        fields = [key for key, val in clsdict.items()
                  if isinstance(val, Descriptor)]

        for name in fields:
            clsdict[name].name = name

        clsobj = super().__new__(cls, clsname, bases, dict(clsdict))

        sig = Signature([Parameter(fname, Parameter.POSITIONAL_OR_KEYWORD)
                         for fname in fields])
        setattr(clsobj, '__signature__', sig)
        return clsobj


class Node(metaclass=MetaNode):  
    _fields = []

    def __init__(self, *args, **kwargs):
        bound_args = self.__signature__.bind(*args, **kwargs)
        for name, val in bound_args.arguments.items():
            setattr(self, name, val)
