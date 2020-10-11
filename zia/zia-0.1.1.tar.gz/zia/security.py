
import json
import logging


class Security(object):
    def __init__(self, session):
        self.session = session
    def get_whitelist_urls(self):
        path = 'security'
        return self.session.get(path)
    def update_whitelist_urls(self):
        raise NotImplementedError()
    def get_blacklist_urls(self):
        path = 'security/advanced'
        return self.session.get(path)
    def update_blacklist_urls(self):
        raise NotImplementedError()
    def add_blacklist_urls(self, black_list_urls):
        path = 'security/advanced/blacklistUrls?action=ADD_TO_LIST'
        body = {
            "blacklistUrls": [
            ]
        }
        for url in black_list_urls:
            body['blacklistUrls'].append(str(url))
        return self.session.post(path, body)
    def remove_blacklist_urls(self):
        raise NotImplementedError()


LOGGER = logging.getLogger(__name__)
