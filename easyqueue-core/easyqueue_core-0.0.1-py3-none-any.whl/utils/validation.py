from typing import Type
from collections.abc import Iterable


class TypeValidator:

    @staticmethod
    def raise_validation_element_type(element_name: str, element: object, type_class: Type, allow_none: bool = False):
        if not isinstance(element, type_class):
            if not (element is None and allow_none):
                raise TypeError(
                    'Invalid type for {elem_name} with value {elem_val}, expected {exp_type}, found {f_type}'.format(
                        elem_name=element_name, elem_val=element, exp_type=type_class, f_type=type(element)))

    @staticmethod
    def raise_validation_element_empty(element_name: str, element: object, allow_none: bool = False):
        if isinstance(element, Iterable):
            if not element and not (element is None and allow_none):
                raise TypeError(
                    'Invalid element {elem_name} with no valid value {elem_val}'.format(
                        elem_name=element_name, elem_val=element))
