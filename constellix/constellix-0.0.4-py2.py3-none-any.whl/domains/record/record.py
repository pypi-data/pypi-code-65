"""Constellix Domain Records"""

import logging
import sys

from . import type as RecordTypes
from .const import RECORD_TYPE_LIST

_LOGGER = logging.getLogger(__name__)


class DomainRecords(object):
    def __init__(self, protocol=None, domain=None):
        super().__init__()
        self.__domain = domain
        self.__protocol = protocol
        self.__records = Records()

    async def all(self):
        if self.__domain is None:
            _LOGGER.warning("Cannot load records when there is no domain")
            return None
        for record_type in RECORD_TYPE_LIST:
            record_type_holder = getattr(RecordTypes, record_type, None)
            records_holder = getattr(self.__records, record_type, None)
            if record_type_holder is None:
                _LOGGER.warning(f"No known handler for type {record_type}")
                continue
            if records_holder is None:
                _LOGGER.warning(f"No known holder for type {record_type}")
                continue
            all_records_of_type = await self.__protocol.api_get(
                path=f"domains/{self.domain_id}/records/{record_type}"
            )
            for record in all_records_of_type:
                if len(record["name"]) > 0:
                    name = record["name"] + f".{self.__domain.name}"
                else:
                    name = self.__domain.name
                records_holder[name] = record_type_holder(
                    protocol=self.__protocol,
                    domain=self.__domain,
                    constellix_payload=record,
                )
            _LOGGER.debug(records_holder)

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
        record_holder = getattr(RecordTypes, record_type, None)

        if not record_holder:
            _LOGGER.warning(f"No known handler for type {record_type}")
            None

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


class Records(object):
    def __init__(self):
        super().__init__()
        for record_type in RECORD_TYPE_LIST:
            setattr(self, record_type, dict())
