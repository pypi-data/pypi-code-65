# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
try:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
except ImportError:
    from pkg_resources import declare_namespace
    declare_namespace(__name__)

from zimupy.base import ZiMuZu
from zimupy.client import api


class ZiMuZuClient(ZiMuZu):

    resource = api.Resource()
    common = api.Common()
    v3 = api.V3()
    base_url = ''

    def __init__(self, access_key, cid, base_url=None):
        if base_url:
            self.base_url = base_url
        else:
            with open('base_url') as s:
                base_url = s.readline()
                self.base_url = base_url
        super(ZiMuZuClient, self).__init__(access_key, cid, base_url=base_url)
