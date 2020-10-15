# -*- coding: utf-8 -*-
__author__ = 'jasonxu'
from abc import ABCMeta, abstractmethod


class Device(metaclass=ABCMeta):

    @abstractmethod
    def take_screenshot(self):
        pass

