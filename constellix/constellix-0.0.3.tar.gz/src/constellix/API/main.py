# -*- coding: utf-8 -*-
import asyncio
import logging
import os

from ..protocol import Protocol
from ..domains import Domains

_LOGGER = logging.getLogger(__name__)


class Constellix(object):
    def __init__(self, api_key=None, secret_key=None, loop=None):
        super().__init__()
        self.__loop = loop if loop else asyncio.get_event_loop()

        if not api_key:
            api_key = os.environ.get("CONSTELLIX_APIKEY")
        if not secret_key:
            secret_key = os.environ.get("CONSTELLIX_APISECRET")

        self.__protocol = Protocol(
            api_key=api_key, secret_key=secret_key, loop=self.__loop
        )
        self.__domains = Domains(protocol=self.__protocol)

    @property
    def domains(self):
        try:
            return self.__domains
        except AttributeError:
            return None
