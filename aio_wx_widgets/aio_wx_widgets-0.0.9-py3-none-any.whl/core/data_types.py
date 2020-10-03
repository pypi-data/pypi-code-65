"""Datatypes used by widgets."""

import logging
from typing import NamedTuple, Any

_LOGGER = logging.getLogger(__name__)


class Choices(NamedTuple):
    """Choice item."""

    label: str
    value: Any
