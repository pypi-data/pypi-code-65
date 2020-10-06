#!/usr/bin/env python

## Standard Lib
from collections import OrderedDict
import logging
import re

## TTILS:
from .terrors import *
from .conf import *

def export(code):
    globals()[code.__name__] = code
    __all__.append(code.__name__)
    return code

__all__ = []

@export
class Descriptor:
    _validator_type = "descriptor"
    
    def __init__(self, name=None):
        self.name = name
    
    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            logging.debug(f"Get attribute {self.name}")
            return instance.__dict__[self.name]
    
    def __set__(self, instance, value):
        logging.debug(f"Set {self.name} {value}")
        instance.__dict__[self.name] = value
    
    def __delete__(self, instance):
        logging.debug(f"Delete {self.name}", )
        del instance.__dict__[self.name]

@export
class Typed(Descriptor):
    '''Typed'''
    #expected type
    ty = object

    def __set__(self, instance, value):
        if not isinstance(value, self.ty):
            raise TypeError(f"Expected {self.ty}")
        else:
            super().__set__(instance, value)

#### Base Field Types
@export
class Integer(Typed):
    '''Integer'''
    ty = int

@export
class Float(Typed):
    '''Float'''
    ty = float

@export
class Complex(Typed):
    '''Complex'''
    ty = complex

@export
class String(Typed):
    '''String'''
    ty = str

@export
class List(Typed):
    '''List'''
    ty = list

@export
class Dict(Typed):
    '''Dict'''
    ty = dict

@export
class Bytes(Typed):
    '''Bytes'''
    ty = bytes

@export
class Tuple(Typed):
    '''Tuple'''
    ty = tuple

#### Base Field Properties
@export
class Negative(Descriptor):
    '''Negative'''
    def __set__(self, instance, value):
        if value > 0:
            raise FieldValidationError("Negative value required.")
        super().__set__(instance, value)


@export
class NonNegative(Descriptor):
    '''NonNegative'''
    def __set__(self, instance, value):
        if value < 0:
            raise FieldValidationError("Non-negative value required.")
        super().__set__(instance, value)


@export
class Positive(Descriptor):
    '''Positive'''
    def __set__(self, instance, value):
        if value <= 0:
            raise FieldValidationError("Positive value required.")
        super().__set__(instance, value)


@export
class Sized(Descriptor):
    '''Sized'''
    def __init__(self, *args, maxlen, **kwargs):
        self.maxlen = maxlen
        super().__init__(*args, **kwargs)

    def __set__(self, instance, value):
        if len(value) > self.maxlen:
            raise FieldValidationError(f"Field must be smaller than length {self.maxlen}" )
        super().__set__(instance, value)


@export
class Regex(Descriptor):
    '''Regex'''
    def __init__(self, *args, pattern, **kwargs):
        self.pattern = re.compile(pattern)
        super().__init__(*args, **kwargs)

    def __set__(self, instance, value):
        if not self.pattern.match(value):
            raise FieldValidationError("Invalid string value")
        super().__set__(instance, value)

#### Composite Fields
@export
class NegativeFloat(Float, Negative):
    '''NegativeFloat'''
    pass


@export
class NonNegativeFloat(Float, NonNegative):
    '''NonNegativeFloat'''
    pass


@export
class PositiveFloat(Float, Positive):
    '''PositiveFloat'''
    pass


@export
class NegativeInteger(Integer, Negative):
    '''NegativeInteger'''
    pass


@export
class NonNegativeInteger(Integer, NonNegative):
    '''NonNegativeInteger'''
    pass


@export
class PositiveInteger(Integer, Positive):
    '''PositiveInteger'''
    pass


@export
class SizedString(String, Sized):
    '''SizedString'''
    pass


@export
class RegexString(String, Regex):
    '''SizedRegexString'''
    pass


@export
class SizedRegexString(SizedString, Regex):
    '''SizedRegexString'''
    pass


@export
class PreciseFloat(Float):
    '''PreciseFloat'''
    def bepsi(self):
        pass


@export
class RegexString(Float):
    '''RegexString'''
    def bepsi(self):
        pass
