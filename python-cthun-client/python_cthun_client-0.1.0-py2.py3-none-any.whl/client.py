# -*- coding: utf-8 -*-
__author__ = 'jasonxu'
from cthun_client.config import Config
from cthun_client.connection import Connection
from cthun_client.device.ios import Ios
from cthun_client.device.android import Android


class Client:
    def __init__(self, config, connection=None):
        self._config = config if config else Config()
        self._connection = connection if connection else Connection(self._config)
        self._ios = Ios
        self._android = Android

    @property
    def connection(self):
        return self._connection

    @property
    def config(self):
        return self._config

    def ios(self, device_id):
        return self._ios(device_id)

    def android(self, device_id):
        return self._android(device_id)

    def get_pos(self, device_client):
        device_client.take_screenshot()

