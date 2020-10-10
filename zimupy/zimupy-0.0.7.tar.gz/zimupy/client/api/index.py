# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from zimupy.client.api.base import BaseZiMuZuAPI


class Index(BaseZiMuZuAPI):

    def index(self):
        url = 'resource/fetchlist'
        params = {}
