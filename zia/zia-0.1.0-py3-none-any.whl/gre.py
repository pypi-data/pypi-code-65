
import logging
from .defaults import *


class Gre(object):
    def __init__(self, session):
        self.session = session
    def get_gre_tunnel_details(self):
        path = 'orgProvisioning/ipGreTunnelInfo'
        return self.get(path)


LOGGER = logging.getLogger(__name__)
