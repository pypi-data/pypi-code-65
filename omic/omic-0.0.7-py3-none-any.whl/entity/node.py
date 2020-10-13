#!/usr/bin/env python3
# -.- coding: utf-8 -.-
"""..."""


from pathlib import Path
import functools
import json
import os

from munch import munchify, Munch
import requests

from omic.client import Client
from omic.global_ import GlobalClient
from omic.parallel import run_parallel 
from omic.util import strict_http_do, check_args, get_cloud, \
                      download_url


__copyright__ = 'Copyright © 2020 Omic'


class NodeClient(Client):
    def __init__(self, config: dict):
        self.config = config

    def create(
        self, 
        name: str,
        environment: str,
        description: str = None,
        instructions: str = None,
        parameters: dict = None,
        hyperparameters: dict = None,
        outparameters: dict = None,
        io: dict = None,
        omic: str = None,
        layer: str = None 
    ):
        data = {
            'name': name,  
            'environment': environment,
            'description': description,
            'instructions': instructions,
            'parameters': parameters,
            'hyperparameters': hyperparameters,
            'outparameters': outparameters,
            'io': io,
            'omic': omic,
            'layer': layer 
        }
        return self._hit(
            'post',
             endpoint=f'{self.config.endpoint}/node',
             json_body=data,
             silent=False
        )._id

    def retrieve(
        self, 
        _id: str = None,
        name: str = None,
        fulfill: bool = None
    ):
        return self._hit(
            'get',
            endpoint=f'{self.config.endpoint}/node',
            qparams=self._build_args(_id=_id, name=name, fulfill=fulfill),
            silent=False
        )

    def delete(
        self, 
        _id: str
    ):
        return self._hit(
            'delete',
            endpoint=f'{self.config.endpoint}/node',
            qparams={'_id': _id}
        )
