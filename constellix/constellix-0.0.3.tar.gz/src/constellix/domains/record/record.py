"""Constellix Domain Records"""

import importlib
import logging
import sys

from .const import RECORD_TYPE_LIST

_LOGGER = logging.getLogger(__name__)


class DomainRecords(object):
    def __init__(self, protocol=None, domain=None):
        super().__init__()
        self.__domain = domain
        self.__protocol = protocol
        self.__records = Records()

    async def all(self):
        for record_type in RECORD_TYPE_LIST:
            all_records_of_type = await self.__protocol.api_get(
                path=f"domains/{self.domain_id}/records/{record_type}"
            )
            _LOGGER.debug(all_records_of_type)

    async def fetch(self, record_type, record_id):
        if not self.domain_id:
            return None
        if not (record_type and record_id):
            return None

        record_type = record_type.upper()

        if not record_type in RECORD_TYPE_LIST:
            return None

        constellix_payload = await self.__protocol.api_get(
            path=f"domains/{self.domain_id}/records/{record_type}/{record_id}"
        )

        if not constellix_payload:
            return None

        existing_records = getattr(self.__records, record_type, dict())
        record_holder = importlib.import_module(f".${record_type}")

        existing_records[constellix_payload["name"]] = record_holder(
            protocol=self.__protocol, constellix_payload=constellix_payload
        )
        return existing_records[constellix_payload["name"]]

    @property
    def domain_id(self):
        try:
            return self.__domain.id
        except AttributeError:
            return None


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


class Records(object):
    def __init__(self):
        super().__init__()
        for record_type in RECORD_TYPE_LIST:
            setattr(self, record_type, dict())
