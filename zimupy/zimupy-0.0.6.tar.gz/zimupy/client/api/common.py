# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from zimupy.client.api.base import BaseZiMuZuAPI


class Common(BaseZiMuZuAPI):

    def search(self,
               query,
               search_type='',
               sort=None,
               limit=None,
               page=None):
        """
        全站搜索
        :param query: 搜索关键词
        :param search_type: 搜索类型,resource-影视资源,subtitle-字幕资源,article-资讯以及影评和剧评.如果为空,则在以上三种资源中搜索
        :param sort: 排序 pubtime发布时间 uptime更新时间    默认为更新时间
        :param limit: 每页数量(默认输出20个)
        :param page: 页码
        :return:
        {
            u'count': 28,
            u'list':
            [
                {
                    u'channel': u'tv',
                    u'itemid': u'33701',
                    u'pubtime': u'1436696701',
                    u'title': u'\u300a\u897f\u90e8\u4e16\u754c\u300b(Westworld 2016)',
                    u'type': u'resource',
                    u'uptime': u'1481284037'
                },
                {
                    u'channel': u'movie',
                    u'itemid': u'29137',
                    u'pubtime': u'1361195165',
                    u'title': u'\u300a\u897f\u90e8\u4e16\u754c\u300b(Westworld)[\u672a\u6765\u4e16\u754c/\u94bb\u77f3\u5bab/\u8840\u6d17\u4e50\u56ed]',
                    u'type': u'resource',
                    u'uptime': u'1475505070'
                },
                {
                    u'channel': u'',
                    u'itemid': u'50724',
                    u'pubtime': u'1480932253',
                    u'title': u'\u300a\u897f\u90e8\u4e16\u754c \u7b2c1\u5b63\u7b2c10\u96c6  \u672c\u5b63\u7ec8\u300b(Westworld S01E10 Season Finale)',
                    u'type': u'subtitle',
                    u'uptime': u'1480932253'
                },
            ]
        }
        """

        url = 'search'
        params = {
            'k': query,
            'st': search_type,
        }
        if sort:
            params.update({'order': sort})
        if limit:
            params.update({'limit': limit})
        if page:
            params.update({'page': page})

        ret = self._get(
            url,
            params=params
        )

        return ret

    def schedule(self, start, end, limit=None):
        """
        美剧时间表
        :param start: 开始时间,标准的时间格式,如:2015-02-03或2015-2-3或20150203
        :param end: 结束时间,同上,开始时间和结束时间不能超过31天
        :param limit: 返回数量
        :return:
        {
            u'2016-12-01': [
                {
                    u'cnname': u'\u72af\u7f6a\u5fc3\u7406',
                    u'enname': u'Criminal Minds',
                    u'episode': u'7',
                    u'id': u'11003',
                    u'poster': u'http://tu.rrsub.com/ftp/2016/1027/a5abe7606f31eca6f83a99564733e5b0.jpg',
                    u'poster_a': u'http://tu.rrsub.com/ftp/2016/1027/a_a5abe7606f31eca6f83a99564733e5b0.jpg',
                    u'poster_b': u'http://tu.rrsub.com/ftp/2016/1027/b_a5abe7606f31eca6f83a99564733e5b0.jpg',
                    u'poster_m': u'http://tu.rrsub.com/ftp/2016/1027/m_a5abe7606f31eca6f83a99564733e5b0.jpg',
                    u'poster_s': u'http://tu.rrsub.com/ftp/2016/1027/s_a5abe7606f31eca6f83a99564733e5b0.jpg',
                    u'season': u'12'
                },
                {
                    u'cnname': u'\u5357\u65b9\u516c\u56ed',
                    u'enname': u'South Park',
                    u'episode': u'9',
                    u'id': u'10490',
                    u'poster': u'http://tu.rrsub.com/ftp/2016/0914/6d2337fe9b114a9f433af67ee0e41cf1.jpg',
                    u'poster_a': u'http://tu.rrsub.com/ftp/2016/0914/a_6d2337fe9b114a9f433af67ee0e41cf1.jpg',
                    u'poster_b': u'http://tu.rrsub.com/ftp/2016/0914/b_6d2337fe9b114a9f433af67ee0e41cf1.jpg',
                    u'poster_m': u'http://tu.rrsub.com/ftp/2016/0914/m_6d2337fe9b114a9f433af67ee0e41cf1.jpg',
                    u'poster_s': u'http://tu.rrsub.com/ftp/2016/0914/s_6d2337fe9b114a9f433af67ee0e41cf1.jpg',
                    u'season': u'20'
                },
            ]
        }
        """
        url = 'tv/schedule'
        params = {
            'start': start,
            'end': end,
        }
        if limit:
            params.update({'limit': limit})

        ret = self._get(
            url,
            params=params
        )

        return ret
