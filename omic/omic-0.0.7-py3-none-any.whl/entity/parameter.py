#!/usr/bin/env python3
# -.- coding: utf-8 -.-


import json

from munch import munchify
import requests

from omic.client import Client


__copyright__ = 'Copyright © 2020 Omic'


class ParameterClient(Client):

    def decode(self, data: str):
        return self._hit(
            'post',
            f'{self.config.endpoint}/parameter/decode', 
            data=data
        )
