# -*- coding: utf-8 -*-
"""
Domains handler for Constellix
"""
import logging
from .domain import Domain

_LOGGER = logging.getLogger(__name__)


class Domains(object):
    def __init__(self, protocol=None):
        super().__init__()
        self.__protocol = protocol if protocol else None
        self.__domains = dict()

    async def all(self):
        all_domains = await self.__protocol.api_get(path="domains")
        for constellix_payload in all_domains:
            if "name" in constellix_payload:
                self.__domains[constellix_payload["name"]] = Domain(
                    protocol=self.__protocol, constellix_payload=constellix_payload
                )
        return self.__domains

    async def fetch(self, domain_id):
        constellix_payload = await self.__protocol.api_get(path=f"domains/{domain_id}")
        if not constellix_payload:
            return None
        self.__domains[constellix_payload["name"]] = Domain(
            protocol=self.__protocol, constellix_payload=constellix_payload
        )
        return self.__domains[constellix_payload["name"]]

    async def create(self, name, template=None):
        payload = {"names": [name]}
        if template:
            payload["template"] = template
        domain_creation = await self.__protocol.api_post(path="domains", json=payload)
        if not (domain_creation and domain_creation[0]):
            return None
        new_domain = domain_creation[0]
        if not new_domain["id"]:
            return None
        return await self.fetch(new_domain["id"])

    async def __search(self, search_type="exact", search=""):
        query = {search_type: search}
        all_domains = await self.__protocol.api_get(path="domains/search", params=query)
        for constellix_payload in all_domains:
            if "name" in constellix_payload:
                self.__domains[constellix_payload["name"]] = Domain(
                    protocol=self.__protocol, constellix_payload=constellix_payload
                )
        return self.__domains

    async def search_startswith(self, search=""):
        return await self.__search(search_type="startswith", search=search)

    async def search_endswith(self, search=""):
        return await self.__search(search_type="endswith", search=search)

    async def search_exact(self, search=""):
        return await self.__search(search_type="exact", search=search)

    async def search(self, search=""):
        return await self.__search(search_type="contains", search=search)
