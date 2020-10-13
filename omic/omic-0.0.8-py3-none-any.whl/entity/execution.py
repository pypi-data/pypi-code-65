#!/usr/bin/env python3
# -.- coding: utf-8 -.-


import json

from munch import munchify, Munch
import requests

from omic.client import Client
from omic.util import strict_http_do
from omic.global_ import GlobalClient


__copyright__ = 'Copyright © 2020 Omic'


class ExecutionClient(Client):
        
    # TODO:  Move to API/core or client.
    def resolve_input(self, ex_input: object) -> dict:
        """Transform script input to reference literal cloud storage."""
        def _filter_rpath(ex_input): 
            if isinstance(ex_input, Munch):
                # Normalize
                ex_input = ex_input.toDict()
            if isinstance(ex_input, list):
                for i in range(len(ex_input)):
                    ex_input[i] = _filter_rpath(ex_input[i])
            elif isinstance(ex_input, dict):
                if '_id' in ex_input:
                    # Detected data
                    return ex_input['rpath']
                else:
                    for k, v in ex_input.items():
                        ex_input[k] = _filter_rpath(v)
            # Otherwise, primitives return themselves.
            return ex_input
        gclient = GlobalClient(self.config)
        ex_input = gclient.fulfill(ex_input)
        filtered = _filter_rpath(ex_input)
        return filtered 
    
    def update_status(self, _id: str, status: str):
        endpoint = '/execution/{_id}/status'
        return self._hit(
            'post',
            endpoint=endpoint, 
            json_body=status
        )

    def add_trace(
        self, 
        _id: str, 
        tracepoint: str = None, 
        struct: dict = None, 
        status: str = None, 
        input: object = None, 
        output: object = None, 
        log: object = None, 
        depth: int = None, 
        stage: int = None
    ):
        endpoint = '/execution/{_id}/trace'
        payload = {}
        if tracepoint:
            payload.update({'tracepoint': tracepoint})
        if struct:
            payload.update({'struct': struct})
        if status:
            payload.update({'status': status})
        if input:
            payload.update({'input': input})
        if output:
            payload.update({'output': output})
        if log:
            payload.update({'log': log})
        if depth is not None:
            payload.update({'depth': depth})
        if stage is not None:
            payload.update({'stage': stage})
        return self._hit('post', endpoint, json_body=payload)

    def retrieve_traces(self, _id: str):
        return self._hit(
            'get',
            endpoint='/execution/{_id}/trace',
            qparams={'user': self.config.user},
        )

    def transfer_inputs(self, data: str):
        endpoint = '/execution/cromwell/transfer'
        qparams = {'user': self.config.user}
        return self._hit(
            'post',
            endpoint=endpoint, 
            qparams=qparams,
            json_body=data
        )

    def retrieve_transferred_inputs(self, _id: str):
        qparams = {'user': self.config.user, '_id': _id}
        endpoint = '/execution/cromwell/transfer'
        return self._hit('get',
                         endpoint=endpoint, 
                         qparams=qparams)

    """Other bioinformatics engines:"""

    def execute_wdl(self, fields: dict, inputs: str):
        return hit('post', 
                   endpoint='/execution/cromwell',
                   qparams={'user': self.config.user}, 
                   headers={'x-api-key': self.config.key},
                   json_body={'inputs': inputs, 'fields': fields})._id

    def retrieve_wdl(self, _id: str) -> Munch:
        """Get cromwell status, output, and logs."""
        results = Munch()
        qparams = {'user': self.config.user, '_id': _id}
        headers = {'x-api-key': self.config.key}
        endpoint = '/execution/cromwell/status'
        results.status = hit('get',
                             endpoint=endpoint,
                             qparams=qparams, 
                             headers=headers).status.lower()
        endpoint = '/execution/cromwell/output'
        results.output = hit('get',
                             endpoint=endpoint,
                             qparams=qparams, 
                             headers=headers).output
        endpoint = '/execution/cromwell/log'
        results.log = hit('get',
                          endpoint=endpoint,
                          qparams=qparams, 
                          headers=headers)
        return results
        
    def delete(self, _id: str):
        pass

    def create(
        self,
        input: dict,
        graph: object = None,
        node: object = None,
        name: str = None,
        queue: str = 'home'
    ):
        endpoint = '/execution'
        payload = {
            'input': input,
            'name': name,
            'queue': queue 
        }
        if node:
            node = node if isinstance(node, str) else node['_id']
            payload.update({'node': node})
        if graph:   
            graph = graph if isinstance(graph, str) else graph['_id']
            payload.update({'graph': graph})
        return self._hit(
            'post',
            endpoint=endpoint,
            json_body=payload
        )._id

    def retrieve(
        self, 
	    _id: str, 
	    fulfill: bool = False, 
	    recurse: bool = False
	):
        endpoint = '/execution'
        return self._hit(
            'get',
            endpoint=endpoint,
            qparams={
            	'_id': _id,
            	'fulfill': fulfill, 
            	'recurse': recurse
            }
        )
