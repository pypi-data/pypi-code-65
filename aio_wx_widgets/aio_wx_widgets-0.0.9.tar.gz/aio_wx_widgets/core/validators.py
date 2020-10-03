"""Validators"""

import logging

_LOGGER = logging.getLogger(__name__)

__all__ = ["int_validator", "float_validator", "all_digits_validator"]


def int_validator(value, force) -> int:
    """Int validator."""
    try:
        converted = int(value)
    except ValueError:
        raise ValidationError("Not a valid integer.")
    if value == str(converted):
        return converted
    raise ValidationError("not a valid integer.")


def float_validator(value, force) -> float:
    """Float validator."""
    try:
        converted = float(value)
    except ValueError:
        raise ValidationError("Not a valid float.")
    if value == str(converted):
        return converted
    if force:
        return converted
    return value


def all_digits_validator(value, force) -> str:
    """All digits validator.

    Only numbers are allowed.
    """
    if value.isdigit():
        return value
    raise ValidationError("Only numbers are allowed.")


class ValidationError(Exception):
    """Input validation error"""
