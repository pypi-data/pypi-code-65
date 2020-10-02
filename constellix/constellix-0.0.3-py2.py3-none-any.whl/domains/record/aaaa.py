"""AAAA Record"""
import logging

from .record import DomainRecord

_LOGGER = logging.getLogger(__name__)


class AAAA(DomainRecord):
    def __init__(self, constellix_payload=None):
        super().__init__()
        self.__record_type = "AAAA"
