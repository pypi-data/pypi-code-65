import os
import sys
import json
import re
import copy
from enrichsdk.contrib.lib.transforms.fileops import FileOperationsBase
import logging

logger = logging.getLogger("app")

class FileOperations(FileOperationsBase):

    @classmethod
    def instantiable(cls):
        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "FileOperations"

        test_root = os.environ['ENRICH_TEST']
        self.testdata = {
            'data_root': os.path.join(test_root, self.name),
            'outputdir': os.path.join(test_root, self.name, 'output'),
            'inputdir': test_root,
            'statedir': os.path.join(test_root, self.name, 'state'),
            'global': {
                'args': {
                    'rundate': '2020-01-10'
                }
            },
	        'conf': {
	            'args': {
                    "actions": [
                        {
                            "action": "copy",
                            "src": "%(output)s/%(runid)s/outputs/cars.csv",
                            "dst": "%(data_root)s/shared/%(rundate)s/hello.csv"
                        }
                    ]
   		        }
	        },
            'data': {
            }
        }


provider = FileOperations
