import os
import sys
import json 
import re 
import copy 
from enrichsdk import Sink
import logging 

logger = logging.getLogger("app") 

class MyJSONSink(Sink): 

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.name = "JSONSink" 

        self.outputs = { 
        }

        self.dependencies = { 
	}

        self.testdata = { 
            'conf': {
                'args': { 
                    'frame1': {
                        'frametype': 'dict', 
                        'filename': '%(data_root)s/JSONSink/mytestoutput.json',
                        'params': {} 
                    }
                }
            },
            'data': { 
                'frame1': {
                    'filename': 'outputjson.json', 
                    'frametype': 'dict', 
                    'transform': 'TestJSON',
                    'params': {
                    }
                }
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
                logger.error("Invalid configuration. Only JSON/Dictionaries are supported by this sink transform", 
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

            detail['root'] = self.config.enrich_data_dir 

            tags = detail.get('tags', [])
            if isinstance(tags, str): 
                tags = [tags] 
            detail['tags'] = tags 

            #=> Materialize the path...
            detail['filename'] = self.config.get_file(detail['filename'],
                                                      extra={
                                                          'frame_name': name 
                                                      })
        
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


        available_frames = state.get_frame_list() 

        # => First construct input for the pandasframe 
        extra = {}
        args_input = {} 
        write_input = {} 
        framecls = self.config.get_dataframe('dict') 
        for pattern in self.args: 
            # The pattern could be precise dataframe name or could be
            # regular expression.
            regex = re.compile('^{}$'.format(pattern))
            frames = [m.group(0) for f in available_frames for m in [regex.search(f)] if m]
            if len(frames) == 0: 
                logger.warning("Pattern has not matched any frames: {}".format(pattern)) 
                continue 

            for f in frames: 

                # Get the details of this frame 
                detail = state.get_frame(f) 

                # Handle frametype
                frametype = detail['frametype'] 
                if frametype != 'dict': 
                    logger.warning("Pattern has matched non-dict frame: {}".format(f),
                                   extra=self.config.get_extra({
                                       'transform': self.name
                                   }))
                    continue 

                # Now construct the output file name 
                filename = self.args[pattern]['filename'] 
                filename = self.config.get_file(filename, 
                                                create_dir=True, 
                                                extra={
                                                    'frame_name': f
                                                }) 

                extra[f] = { 
                    'notes': self.collapse_notes(detail),
                    'descriptions': self.collapse_descriptions(detail)
                }

                params = self.args[pattern].get('params',{})
                write_input[f] = { 
                    'frametype': detail['frametype'], 
                    'filename': filename, 
                    'pattern': pattern, 
                    'df': detail['df'],
                    'params': params 
                }

                args_input[f] = copy.copy(self.args[pattern]) 
                args_input[f]['filename'] = filename 
        
        framecls.write(args_input, write_input) 

        for name in write_input: 
            
            detail = write_input[name] 

            # => Insert columns and tags
            pattern = detail['pattern'] 
            detail['params']['tags'] = self.args[pattern]['tags'] 

            # Incorporate columns, notes and description 
            detail['params'].update(extra[name]) 

            detail['params'] = [
                detail['params'],
                {
                    'type': 'lineage',
                    'transform': self.name,
                    'dependencies': [
                        {
                            'type': 'dataframe',
                            'nature': 'input',
                            'objects': [
                                name
                            ]
                        },
                        {
                            'type': 'file',
                            'nature': 'output',
                            'objects': [
                                detail['params']['filename']
                            ]
                        }
                    ]
                }
            ]

            # Insert additional detail 
            detail['transform'] = self.name 
            detail['history'] = [
                {
                    'transform': self.name, 
                    'log': "Wrote output"
                }
            ]

            state.update_frame(name, detail) 

        logger.debug("Finished writing data", 
                     extra=self.config.get_extra({
                         'transform': self.name 
                     }))

        ###########################################
        # => Return 
        ###########################################
        return state 

    def validate_results(self, what, state): 
        """
        Check to make sure that the execution completed correctly
        """
        pass 

        
provider = MyJSONSink 
