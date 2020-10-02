"""A Record"""
import logging

from .record import DomainRecord

_LOGGER = logging.getLogger(__name__)


class A(DomainRecord):
    def __init__(self, protocol=None, constellix_payload=None):
        super().__init__()
        self.__record_type = "A"
