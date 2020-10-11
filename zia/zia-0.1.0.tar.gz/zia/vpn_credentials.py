import random
import string
import json
import logging
from .defaults import *


class VpnCredentials(object):
    def __init__(self, session):
        self.session = session
    def _randomize_psk(self):
        psk = ''.join(random.choices(
            string.ascii_letters + string.digits, k=MAX_PSK_LEN))
        LOGGER.debug("RANDOM PSK: {} (PSK Length: {})".format(
            psk,
            len(psk)
        ))
        return psk
    def extract_vpn_credential_id(self, json_response):
        data = json.loads(json_response)
        LOGGER.debug("Extract VPN ID: {}".format(data['id']))
        return data['id']
    def get_vpn_credentials(self):
        path = 'vpnCredentials'
        return self.session.get(path)
    def create_vpn_credential(self, fqdn, psk):
        path = 'vpnCredentials'
        if not fqdn:
            LOGGER.error("ERROR: {}".format("No FQDN Provided"))
            return 'No FQDN Provided'
        if psk:
            LOGGER.debug("PREDEFINED PSK: {}".format(psk))
        elif not psk:
            psk = self._randomize_psk()
        body = {
            'type': 'UFQDN',
            'fqdn': fqdn,
            'comments': 'Zscaler SDK',
            'preSharedKey': psk
        }
        return self.session.post(uri, body)
    def get_vpn_credential_by_id(self, vpn_id):
        path = 'vpnCredentials/' + str(vpn_id)
        return self.session.get(path)
    def update_vpn_credential_by_id(self, vpn_id, fqdn, psk):
        path = 'vpnCredentials/' + str(vpn_id)
        if not fqdn:
            LOGGER.error("ERROR: {}".format("No FQDN Provided"))
            return 'No FQDN Provided'
        if psk:
            LOGGER.debug("PREDEFINED PSK: {}".format(psk))
        elif not psk:
            psk = self._randomize_psk()
        body = {
            'type': 'UFQDN',
            'fqdn': fqdn,
            'comments': 'Zscaler SDK',
            'preSharedKey': psk
        }
        return self.session.put(path, body)
    def delete_vpn_credential_by_id(self, vpn_id):
        path = 'vpnCredentials/' + vpn_id
        return self.session.delete(path)


LOGGER = logging.getLogger(__name__)
