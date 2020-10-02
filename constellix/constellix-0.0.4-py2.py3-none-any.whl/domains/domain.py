"""
Domains handler for Constellix
"""
import logging
from datetime import datetime
from .record import *

_LOGGER = logging.getLogger(__name__)
_CONSTELLIX_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class Domain(object):
    def __init__(self, protocol=None, constellix_payload=None):
        super().__init__()
        self.__protocol = protocol
        self.__records = DomainRecords(protocol=self.__protocol, domain=self)
        self.__soa = (
            SOA(protocol=self.__protocol, constellix_payload=constellix_payload["soa"])
            if "soa" in constellix_payload
            else None
        )
        self.__id = (
            int(constellix_payload["id"]) if "id" in constellix_payload else None
        )
        self.__name = (
            constellix_payload["name"] if "name" in constellix_payload else None
        )
        self.__created = (
            datetime.strptime(
                constellix_payload["createdTs"], _CONSTELLIX_DATETIME_FORMAT
            )
            if "createdTs" in constellix_payload
            else None
        )
        self.__modified = (
            datetime.strptime(
                constellix_payload["modifiedTs"], _CONSTELLIX_DATETIME_FORMAT
            )
            if "modifiedTs" in constellix_payload
            else None
        )
        self.__type_id = (
            int(constellix_payload["typeId"])
            if "typeId" in constellix_payload
            else None
        )
        self.__domain_tags = (
            constellix_payload["domainTags"]
            if "domainTags" in constellix_payload
            else None
        )
        self.__folder = (
            constellix_payload["folder"] if "folder" in constellix_payload else None
        )
        self.__has_gtd_regions = (
            constellix_payload["hasGtdRegions"]
            if "hasGtdRegions" in constellix_payload
            else None
        )
        self.__has_geo_ip = (
            constellix_payload["hasGeoIP"] if "hasGeoIP" in constellix_payload else None
        )
        self.__vanity_nameserver_id = (
            int(constellix_payload["vanityNameServer"])
            if "vanityNameServer" in constellix_payload
            else None
        )
        self.__vanity_nameserver_name = (
            constellix_payload["vanityNameServerName"]
            if "vanityNameServerName" in constellix_payload
            else None
        )
        self.__nameserver_group_id = (
            int(constellix_payload["nameserverGroup"])
            if "nameserverGroup" in constellix_payload
            else None
        )
        self.__nameservers = (
            constellix_payload["nameservers"]
            if "nameservers" in constellix_payload
            else None
        )
        self.__vanity_name_server_details = (
            VanityNameserver(
                protocol=self.__protocol,
                constellix_payload=constellix_payload["vanityNameServerDetails"],
            )
            if "vanityNameServerDetails" in constellix_payload
            else None
        )
        self.__note = (
            constellix_payload["note"] if "note" in constellix_payload else None
        )
        self.__version = (
            int(constellix_payload["version"])
            if "version" in constellix_payload
            else None
        )
        self.__status = (
            constellix_payload["status"] if "status" in constellix_payload else None
        )
        self.__tags = (
            constellix_payload["tags"] if "tags" in constellix_payload else None
        )
        self.__contact_ids = (
            constellix_payload["contactIds"]
            if "contactIds" in constellix_payload
            else None
        )

    async def delete(self):
        if not self.__id:
            return None

        constellix_payload = await self.__protocol.api_delete(
            path=f"domains/{self.__id}"
        )
        if not constellix_payload:
            return None

        if not "success" in constellix_payload:
            return False

        return True

    @property
    def records(self):
        try:
            return self.__records
        except AttributeError:
            return None

    @property
    def soa(self):
        try:
            return self.__soa
        except AttributeError:
            return None

    @property
    def id(self):
        try:
            return self.__id
        except AttributeError:
            return None

    @property
    def name(self):
        try:
            return self.__name
        except AttributeError:
            return None

    @property
    def created(self):
        try:
            return self.__created
        except AttributeError:
            return None

    @property
    def modified(self):
        try:
            return self.__modified
        except AttributeError:
            return None

    @property
    def type_id(self):
        try:
            return self.__type_id
        except AttributeError:
            return None

    @property
    def domain_tags(self):
        try:
            return self.__domain_tags
        except AttributeError:
            return None

    @property
    def folder(self):
        try:
            return self.__folder
        except AttributeError:
            return None

    @property
    def has_gtd_regions(self):
        try:
            return self.__has_gtd_regions
        except AttributeError:
            return None

    @property
    def has_geo_ip(self):
        try:
            return self.__has_geo_ip
        except AttributeError:
            return None

    @property
    def vanity_nameserver_id(self):
        try:
            return self.__vanity_nameserver_id
        except AttributeError:
            return None

    @property
    def vanity_nameserver_name(self):
        try:
            return self.__vanity_nameserver_name
        except AttributeError:
            return None

    @property
    def nameserver_group_id(self):
        try:
            return self.__nameserver_group_id
        except AttributeError:
            return None

    @property
    def nameservers(self):
        try:
            return self.__nameservers
        except AttributeError:
            return None

    @property
    def vanity_name_server_details(self):
        try:
            return self.__vanity_name_server_details
        except AttributeError:
            return None

    @property
    def note(self):
        try:
            return self.__note
        except AttributeError:
            return None

    @property
    def version(self):
        try:
            return self.__version
        except AttributeError:
            return None

    @property
    def status(self):
        try:
            return self.__status
        except AttributeError:
            return None

    @property
    def tags(self):
        try:
            return self.__tags
        except AttributeError:
            return None

    @property
    def contact_ids(self):
        try:
            return self.__contact_ids
        except AttributeError:
            return None


class SOA(object):
    def __init__(self, protocol=None, constellix_payload=None):
        super().__init__()
        self.__protocol = protocol
        self.__primary_nameserver = (
            constellix_payload["primaryNameserver"]
            if "primaryNameserver" in constellix_payload
            else None
        )
        self.__email = (
            constellix_payload["email"] if "email" in constellix_payload else None
        )
        self.__ttl = (
            int(constellix_payload["ttl"]) if "ttl" in constellix_payload else None
        )
        self.__serial = (
            int(constellix_payload["serial"])
            if "serial" in constellix_payload
            else None
        )
        self.__refresh = (
            int(constellix_payload["refresh"])
            if "refresh" in constellix_payload
            else None
        )
        self.__expire = (
            int(constellix_payload["expire"])
            if "expire" in constellix_payload
            else None
        )
        self.__neg_cache = (
            constellix_payload["negCache"] if "negCache" in constellix_payload else None
        )

    @property
    def primary_nameserver(self):
        try:
            return self.__primary_nameserver
        except AttributeError:
            return None

    @property
    def email(self):
        try:
            return self.__email
        except AttributeError:
            return None

    @property
    def ttl(self):
        try:
            return self.__ttl
        except AttributeError:
            return None

    @property
    def serial(self):
        try:
            return self.__serial
        except AttributeError:
            return None

    @property
    def refresh(self):
        try:
            return self.__refresh
        except AttributeError:
            return None

    @property
    def expire(self):
        try:
            return self.__expire
        except AttributeError:
            return None

    @property
    def neg_cache(self):
        try:
            return self.__neg_cache
        except AttributeError:
            return None


class VanityNameserver(object):
    def __init__(self, protocol=None, constellix_payload=None):
        super().__init__()
        self.__protocol = protocol
        self.__id = (
            int(constellix_payload["id"]) if "id" in constellix_payload else None
        )
        self.__name = (
            constellix_payload["name"] if "name" in constellix_payload else None
        )
        self.__is_default = (
            constellix_payload["isDefault"]
            if "isDefault" in constellix_payload
            else None
        )
        self.__is_public = (
            constellix_payload["isPublic"] if "isPublic" in constellix_payload else None
        )
        self.__nameservers = (
            constellix_payload["nameservers"]
            if "nameservers" in constellix_payload
            else None
        )
        self.__nameserver_group_id = (
            int(constellix_payload["nameserverGroup"])
            if "nameserverGroup" in constellix_payload
            else None
        )
        self.__nameserver_group_name = (
            constellix_payload["nameserverGroupName"]
            if "nameserverGroupName" in constellix_payload
            else None
        )
        self.__nameservers_list_string = (
            constellix_payload["nameserversListString"]
            if "nameserversListString" in constellix_payload
            else None
        )

    @property
    def id(self):
        try:
            return self.__id
        except AttributeError:
            return None

    @property
    def name(self):
        try:
            return self.__name
        except AttributeError:
            return None

    @property
    def is_default(self):
        try:
            return self.__is_default
        except AttributeError:
            return None

    @property
    def is_public(self):
        try:
            return self.__is_public
        except AttributeError:
            return None

    @property
    def nameservers(self):
        try:
            return self.__nameservers
        except AttributeError:
            return None

    @property
    def nameserver_group_id(self):
        try:
            return self.__nameserver_group_id
        except AttributeError:
            return None

    @property
    def nameserver_group_name(self):
        try:
            return self.__nameserver_group_name
        except AttributeError:
            return None

    @property
    def nameservers_list_string(self):
        try:
            return self.__nameservers_list_string
        except AttributeError:
            return None