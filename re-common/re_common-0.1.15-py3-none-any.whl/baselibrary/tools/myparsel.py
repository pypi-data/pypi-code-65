# -*- coding: utf-8 -*-
# @Time    : 2020/9/16 13:18
# @Author  : suhong
# @File    : mcss.py
# @Software: PyCharm
from parsel import Selector


class MParsel(object):
    def __init__(self, logger=None):
        if logger is None:
            from re_common.baselibrary import MLogger
            logger = MLogger().streamlogger
        self.logger = logger

    def css_parsel_html(self, html="", css_selector={}):
        if html != "" and css_selector:
            sel = Selector(html)
            dict_ = dict()
            for key, value in css_selector.items():
                dict_[key] = sel.css(value).getall()
            return True, dict_
        else:
            return False, ""

    def xpath_parsel_html(self, html="", xpath_selector={}):
        if html != "" and xpath_selector:
            sel = Selector(html)
            dict_ = dict()
            for key, value in xpath_selector.items():
                dict_[key] = sel.xpath(value).getall()
            return True, dict_
        else:
            return False, ""

    def asd(self):
        pass
