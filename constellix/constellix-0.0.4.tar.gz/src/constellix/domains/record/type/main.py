"""A Record"""
import logging

_LOGGER = logging.getLogger(__name__)


class DomainRecord(object):
    def __init__(self, protocol=None, domain=None):
        super().__init__()
        self.__protocol = protocol
        self.__domain = domain

    @property
    def record_type(self):
        try:
            return self.__record_type
        except AttributeError:
            return None

    @property
    def domain_id(self):
        try:
            return self.__domain.id
        except AttributeError:
            return None