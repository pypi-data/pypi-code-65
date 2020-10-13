#!/usr/bin/env python3
# -.- coding: utf-8 -.-

import json

from munch import munchify
import fastjsonschema

from omic.const import *
from omic.entity.execution import ExecutionClient
from omic.entity.environment import EnvironmentClient
from omic.entity.graph import GraphClient
from omic.entity.data import DataClient
from omic.entity.node import NodeClient
from omic.global_ import GlobalClient

__copyright__ = 'Copyright © 2020 Omic'

omic_config = {
    #'endpoint': DEVEL_ENDPOINT,
    'endpoint': LOCAL_ENDPOINT,
    #'endpoint': PROD_ENDPOINT,
    'key': None 
}

class Omic:
    def __init__(self, config: dict = {}, store_global: bool = False):
        global omic_config
        self.config = munchify(omic_config)
        self.config.update(config)
        if store_global:
            omic_config = self.config

    def hi(self):
        print(r"""
      ___           ___     
     /\  \         /\__\    
    /::\  \       /::|  |   
   /:/\:\  \     /:|:|  |   
  /:/  \:\  \   /:/|:|__|__ 
 /:/__/ \:\__\ /:/ |::::\__\
 \:\  \ /:/  / \/__/~~/:/  /
  \:\  /:/  /        /:/  / 
   \:\/:/  /        /:/  /  
    \::/  /        /:/  /   
     \/__/         \/__/    
                  ___       
      ___        /\  \      
     /\  \      /::\  \     
     \:\  \    /:/\:\  \    
     /::\__\  /:/  \:\  \   
  __/:/\/__/ /:/__/ \:\__\  
 /\/:/  /    \:\  \  \/__/  
 \::/__/      \:\  \        
  \:\__\       \:\  \       
   \/__/        \:\__\      
                 \/__/      

was here.
""")

    def configure(self, config: dict):
        """Validate and bind configuration."""
        schema = json.loads('''{
            "id": "/OmicConfig",
            "type": "object",
            "properties": {
                "user": { "type": "string" },
                "key": {
                    "anyOf": [
                        { "type": "string" },
                        { "type": "null" }
                    ]
                },
                "endpoint": { "type": "string" }
            },
            "required": ["user"]
        }''')
        self.config.update(config)
        res = fastjsonschema.compile(schema)(self.config)
        return self

    def client(self, client_type: str = None):
        """Return requested client type."""
        client_lookup = {
            'data': DataClient,
            'environment': EnvironmentClient,
            'execution': ExecutionClient,
            'graph': GraphClient,
            'node': NodeClient
        }
        if client_type not in client_lookup:
            return GlobalClient(self.config)
        return client_lookup[client_type](self.config)
