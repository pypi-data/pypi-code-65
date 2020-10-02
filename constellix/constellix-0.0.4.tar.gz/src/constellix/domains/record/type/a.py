"""A Record"""
import logging

from . import DomainRecord

_LOGGER = logging.getLogger(__name__)


class A(DomainRecord):
    def __init__(self, protocol=None, domain=None, constellix_payload=None):
        super().__init__(protocol=protocol, domain=domain)
        self.__id = constellix_payload["id"] if "id" in constellix_payload else None
        self.__type = (
            constellix_payload["type"] if "type" in constellix_payload else None
        )
        self.__record_type = (
            constellix_payload["recordType"]
            if "recordType" in constellix_payload
            else None
        )
        self.__name = (
            constellix_payload["name"] if "name" in constellix_payload else None
        )
        self.__record_option = (
            constellix_payload["recordOption"]
            if "recordOption" in constellix_payload
            else None
        )
        self.__no_answer = (
            constellix_payload["noAnswer"] if "noAnswer" in constellix_payload else None
        )
        self.__disabled = (
            constellix_payload["disabled"] if "disabled" in constellix_payload else None
        )
        self.__note = (
            constellix_payload["note"] if "note" in constellix_payload else None
        )
        self.__ttl = constellix_payload["ttl"] if "ttl" in constellix_payload else None
        self.__gtd_region = (
            constellix_payload["gtdRegion"]
            if "gtdRegion" in constellix_payload
            else None
        )
        self.__parent_id = (
            constellix_payload["parentId"] if "parentId" in constellix_payload else None
        )
        self.__parent = (
            constellix_payload["parent"] if "parent" in constellix_payload else None
        )
        self.__source = (
            constellix_payload["source"] if "source" in constellix_payload else None
        )
        self.__modified_ts = (
            constellix_payload["modifiedTs"]
            if "modifiedTs" in constellix_payload
            else None
        )
        self.__value = (
            constellix_payload["value"] if "value" in constellix_payload else None
        )
        self.__roundRobin = (
            constellix_payload["roundRobin"]
            if "roundRobin" in constellix_payload
            else None
        )
        self.__geolocation = (
            constellix_payload["geolocation"]
            if "geolocation" in constellix_payload
            else None
        )
        self.__record_failover = (
            constellix_payload["recordFailover"]
            if "recordFailover" in constellix_payload
            else None
        )
        self.__failover = (
            constellix_payload["failover"] if "failover" in constellix_payload else None
        )
        self.__round_robin_failover = (
            constellix_payload["roundRobinFailover"]
            if "roundRobinFailover" in constellix_payload
            else None
        )

    @property
    def id(self):
        try:
            return self.__id
        except AttributeError:
            return None

    @property
    def record_type(self):
        try:
            return self.__record_type
        except AttributeError:
            return None

    @property
    def name(self):
        try:
            return self.__name
        except AttributeError:
            return None

    @property
    def record_option(self):
        try:
            return self.__record_option
        except AttributeError:
            return None

    @property
    def no_answer(self):
        try:
            return self.__no_answer
        except AttributeError:
            return None

    @property
    def disabled(self):
        try:
            return self.__disabled
        except AttributeError:
            return None

    @property
    def note(self):
        try:
            return self.__note
        except AttributeError:
            return None

    @property
    def ttl(self):
        try:
            return self.__ttl
        except AttributeError:
            return None

    @property
    def gtd_region(self):
        try:
            return self.__gtd_region
        except AttributeError:
            return None

    @property
    def parent_id(self):
        try:
            return self.__parent_id
        except AttributeError:
            return None

    @property
    def parent(self):
        try:
            return self.__parent
        except AttributeError:
            return None

    @property
    def source(self):
        try:
            return self.__source
        except AttributeError:
            return None

    @property
    def modified_ts(self):
        try:
            return self.__modified_ts
        except AttributeError:
            return None

    @property
    def value(self):
        try:
            return self.__value
        except AttributeError:
            return None

    @property
    def roundRobin(self):
        try:
            return self.__roundRobin
        except AttributeError:
            return None

    @property
    def geolocation(self):
        try:
            return self.__geolocation
        except AttributeError:
            return None

    @property
    def record_failover(self):
        try:
            return self.__record_failover
        except AttributeError:
            return None

    @property
    def failover(self):
        try:
            return self.__failover
        except AttributeError:
            return None

    @property
    def round_robin_failover(self):
        try:
            return self.__round_robin_failover
        except AttributeError:
            return None
