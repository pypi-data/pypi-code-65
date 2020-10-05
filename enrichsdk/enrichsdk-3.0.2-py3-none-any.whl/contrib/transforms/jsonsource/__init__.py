import os
import sys
import json 
from enrichsdk import Source
import logging 

logger = logging.getLogger("app") 

class MyJSONSource(Source): 

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.name = "JSONSource" 

        self.outputs = { 
        }

        self.dependencies = { 
	}

        self.testdata = { 
            'conf': {
                'args': {
                    'hello': { 
                        'filename': '%(data_root)s/TestJSON/hello.json',
                        'frametype': 'dict', 
                        'params': {
                        }
                    }
                }
            },
            'data': { 
            }
        }

    
    def preload_clean_args(self, args): 
        """
        Clean when the spec is loaded...
        """
        # Sanity check...
        assert isinstance(args, dict)

        for name, detail  in args.items(): 

            if (("frametype" not in detail) or 
                (detail['frametype'] != 'dict')): 
                logger.error("Invalid configuration. Only JSON source supported by this source transform", 
                             extra=self.config.get_extra({
                                 'transform': self.name
                             }))
                raise Exception("Invalid configuration")

            if (('filename' not in detail) or 
                (not isinstance(detail['filename'], str)) or 
                ('params' not in detail) or 
                (not isinstance(detail['params'], dict))): 
                logger.error("Invalid args. Filename (string) and params (dict) are required", 
                             extra=self.config.get_extra({
                                 'transform': self.name
                             }))
                raise Exception("Invalid configuration")

            filename = detail['filename'] 
            if not filename.lower().endswith('.json'): 
                logger.error("Input file must a .json file", 
                             extra=self.config.get_extra({
                                 'transform': self.name
                             }))
                raise Exception("Invalid configuration")

            #=> Materialize the path...
            detail['filename'] = self.config.get_file(detail['filename']) 
        
        return args

    def validate_args(self, what, state): 

        assert isinstance(self.args, dict) 
        for name, detail  in self.args.items(): 
            assert (('frametype' in detail) and (detail['frametype'] == 'dict'))
            assert 'filename' in detail
            assert 'params' in detail 

    def process(self, state): 
        """
        Run the computation and update the state 
        """
        logger.debug("{} - process".format(self.name),
                     extra=self.config.get_extra({
                         'transform': self.name 
                     }))

        for name, detail  in self.args.items(): 
            
            filename = detail['filename']             
            data = json.load(open(filename))

            updated_detail = { 
                'df': data,
                'transform': self.name, 
                'frametype': 'dict', 
                'params': [
                    {
                        'type': 'compute',
                    },
                    {
                        'type': 'lineage',
                        'transform': self.name,
                        'dependencies': [
                            {
                                'type': 'file',
                                'nature': 'input',
                                'objects': [
                                    filename
                                ]
                            }
                        ]
                    }
                ], 
                'history': [
                    # Add a log entry describing the change 
                    {
                        'transform': self.name, 
                        'log': 'Loaded json file'
                    }
                ]
            }


            # Update the state. 
            state.update_frame(name, updated_detail, create=True) 
        
        ###########################################
        # => Return 
        ###########################################
        return state 

    def validate_results(self, what, state): 
        """
        Check to make sure that the execution completed correctly
        """

        for name, detail  in self.args.items(): 
            if not state.reached_stage(name, self.name): 
                raise Exception("Could not find new frame created for {}".format(name))
            
                detail = state.get_frame(name) 
                df = detail['df'] 

                # Check if it is a valid dictionary...
                assert isinstance(df, dict) 

        
provider = MyJSONSource 
