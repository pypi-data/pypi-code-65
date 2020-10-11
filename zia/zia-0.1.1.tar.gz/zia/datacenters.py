import logging
from .defaults import *


class Datacenters(object):
    def __init__(self, session):
        self.session = session
    def get_all_vips(self):
        path = 'vips?include=all'
        return self.session.get(path)
    def get_all_public_vips(self):
        path = 'vips?include=public'
        return self.session.get(path)
    def get_all_private_vips(self):
        path = 'vips?include=private'
        return self.session.get(path)


LOGGER = logging.getLogger(__name__)
