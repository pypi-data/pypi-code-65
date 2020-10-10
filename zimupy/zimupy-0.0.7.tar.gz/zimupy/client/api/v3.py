# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from zimupy.client.api.base import BaseZiMuZuAPI


class V3(BaseZiMuZuAPI):

    def resource_storage(self,
                         area='',
                         category='',
                         channel='',
                         limit=20,
                         page=1,
                         order='itemupdate'):
        """
        资源更新列表
        :param area: 地区
        :param category: 类目
        :param channel: 频道
        :param limit: 每页数量
        :param page: 当前页
        :param order: 排序 更新时间:itemupdate

        [{u'area': u'\u7f8e\u56fd',
            u'category': u'\u5267\u60c5',
            u'channel': u'tv',
            u'cnname': u'\u5bcc\u8d35\u903c\u4eba',
            u'enname': u'Filthy Rich',
            u'id': u'40858',
            u'itemupdate': u'1601354289',
            u'play_status': u'\u7b2c1\u5b63\u8fde\u8f7d\u4e2d',
            u'poster': u'http://tu.jstucdn.com/ftp/2020/0918/bc98115277565b76b284e6ef1b4ac33e.png',
            u'poster_b': u'http://tu.jstucdn.com/ftp/2020/0918/b_bc98115277565b76b284e6ef1b4ac33e.png',
            u'poster_m': u'http://tu.jstucdn.com/ftp/2020/0918/m_bc98115277565b76b284e6ef1b4ac33e.png',
            u'poster_s': u'http://tu.jstucdn.com/ftp/2020/0918/s_bc98115277565b76b284e6ef1b4ac33e.png',
            u'publish_year': u'2020',
            u'rank': u'2985',
            u'score': u'7.7',
            u'tvstation': u'FOX',
            u'views': u'27353'}
            ]
        """

        params = {}
        params.update({'a': 'resource_storage'})

        ret = self._get(
            '',
            params=params
        )

        return ret

    def resource(self,
                 resource_id,
                 token,
                 uid):

        params = {}
        params.update({
            'a': 'resource',
            'id': resource_id,
            'token': token,
            'uid': uid
        })

        ret = self._get(
            '',
            params=params
        )

        return ret

    def resource_item(self,
                      resource_id,
                      season,
                      episode,
                      token,
                      uid):

        params = {}
        params.update({
            'a': 'appstore_resource_item',
            'id': resource_id,
            'season': season,
            'episode': episode,
            'token': token,
            'uid': uid
        })

        ret = self._get(
            '',
            params=params
        )

        return ret

    def login(self,
              account,
              password,
              g='api/public',
              m='v2',
              client='1'):

        params = {}
        params.update({
            'a': 'login',
            'account': account,
            'password': password,
            'g': g,
            'm': m,
            'client': client
        })

        ret = self._get(
            '',
            params=params
        )

        return ret

