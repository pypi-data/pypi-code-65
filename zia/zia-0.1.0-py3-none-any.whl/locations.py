import logging
import json

from .defaults import *

class Locations(object):
    def __init__(self, session):
        self.session = session
    def get_locations(self):
        path = 'locations'
        return self.session.get(path)
    def create_location(self, location_name, vpn_cred_id, fqdn, gateway_options=None):
        path = 'locations'
        if not vpn_cred_id:
            return 'VPN Credential ID Required'
        if not fqdn:
            return 'FQDN Required'
        body = {
            "name": location_name,
            "vpnCredentials": [
                {
                    "id": vpn_cred_id,
                    "type": "UFQDN",
                    "fqdn": fqdn
                }
            ]
        }
        if gateway_options:
            body = {**body, **gateway_options}
        return self.session.post(path, body)
    def create_sub_location(self, parent_id, location_name, ip_addresses, gateway_options=None):
        path = 'locations'
        if not parent_id:
            raise RuntimeError('Location Parent ID Required')
        if not location_name:
            raise RuntimeError('Location Name Required')
        if not ip_addresses:
            raise RuntimeError('IP Addresses Required')
        body = {
            "name": location_name,
            "parentId": parent_id,
            "ipAddresses": [
                ip_addresses
            ],
        }
        if gateway_options:
            body = {**body, **gateway_options}
        return self.session.post(path,body)
    def get_locations_lite(self):
        path = 'locations/lite'
        res = self.session.get(path)
        return res.json()
    def get_locations_by_id(self, location_id):
        if not location_id:
            return "Location Requried"
        path = 'locations/lite/' + str(location_id)
        return self.session.get(path)
    def update_location_by_id(self, location_id):
        raise NotImplementedError()
    def delete_location_by_id(self, location_id):
        raise NotImplementedError()
    def get_vpn_endpoints(self, ipv4_addr):
        raise RuntimeError('これセッションである必要があるの? エンドポイントがおかしくないか?')
        if not ipv4_addr:
            return 'IPv4 Address Requried'
        uri = 'https://pac.zscalerbeta.net/getVpnEndpoints?srcIp=' + ipv4_addr
        return self.session.sessionget(uri)


LOGGER = logging.getLogger(__name__)
