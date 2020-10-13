#!/usr/bin/env python3
# -.- coding: utf-8 -.-


import json

from munch import munchify, Munch
import requests

from omic.client import Client


__copyright__ = 'Copyright © 2020 Omic'


class GraphClient(Client):

    def __init__(self, config: dict):
        self.config = config

    def retrieve(
        self, 
        _id: str = None, 
        fulfill: bool = False, 
        recurse: bool = False
    ) -> Munch:
        qparams = {} if not _id else {
            '_id': _id,
            'fulfill': fulfill,
            'recurse': recurse
        }
        return self._hit(
            'get',
            '/graph',
            qparams=qparams
        )

    def delete(self, _id: str) -> None:
        self._hit('delete', '/graph', qparams={'_id': _id})

    def create(
        self,
        name: str,
        parameters: dict,
        entry: str = None, 
        structure: dict = None,
        nodes: list = [],
        labels: list = [],
        hyperparameters: dict = {},
        description: str = None,
        # TODO:  Better...
        source: str = 'dockerpal',
        meta: dict = {'label': 'recipe'}
    ) -> str:
        return self._hit(
            'post',
            '/graph',
            json_body={
                'name': name, 
                'description': description,
                'entry': entry, 
                'structure': structure,
                'parameters': parameters,
                'hyperparameters': hyperparameters,
                'nodes': nodes,
                'labels': labels,
                'source': source,
                'meta': meta
            }
        )._id
