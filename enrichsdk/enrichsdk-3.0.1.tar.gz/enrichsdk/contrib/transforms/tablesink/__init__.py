import os
import sys
import copy
import json
import re
from enrichsdk import Sink
import logging

logger = logging.getLogger("app")

class TableSink(Sink):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "TableSink"

        self.testdata = {
            'conf': {
                'args': {
                    "cars": {
                        "frametype": "pandas",
                        "filename": "%(output)s/cars_revised.csv",
                        "params": {
                            "sep": ","
                        }
                    }
                }
	    },
            'data': {
                "carmodel": {
                    "transform": "CarModel",
                    "filename": "cars.csv",
                    "params": {
                        "sep": ","
                    },
                    "state": {
                        "params": [
                            {
                                'type': 'args',
                                'transform': 'TableSink',
                                'args': {
                                    'save': False,
                                    'rows': 124
                                }
                            }
                        ]
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
        assert len(args) > 0

        for pattern, detail  in args.items():

            if (("type" in detail) and
                ("frametype" not in detail) and
                (detail['type'] == 'table')):
                detail['frametype'] = 'pandas'

            if (("frametype" not in detail) or
                (detail['frametype'] != 'pandas')):
                logger.error("Invalid configuration. Only pandas table source supported by this sink transform",
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

            detail['root'] = self.config.enrich_data_dir

            tags = detail.get('tags', [])
            if isinstance(tags, str):
                tags = [tags]
            detail['tags'] = tags

            sortcols = detail.get('sort', [])
            if isinstance(sortcols, str):
                sortcols = [sortcols]
            detail['sort'] = sortcols

        return args

    def validate_args(self, what, state):

        assert isinstance(self.args, dict)
        for pattern, detail  in self.args.items():
            assert (('frametype' in detail) and (detail['frametype'] == 'pandas'))
            assert 'filename' in detail
            assert 'params' in detail


    def process(self, state):
        """
        Store the file...
        """
        available_frames = state.get_frame_list()

        # => First construct input for the pandasframe
        extra = {}
        write_input = {}
        args_input = {}
        framecls = self.config.get_dataframe('pandas')
        skipped = []
        for pattern in self.args:
            # The pattern could be precise dataframe name or could be
            # regular expression.
            regex = re.compile('^{}$'.format(pattern))
            frames = [m.group(0) for f in available_frames for m in [regex.search(f)] if m]

            for f in frames:
                # For each dataframe that is in the system

                detail = state.get_frame(f)

                # => Are there any extra instructions?
                overrides = self.frame_get_overrides(detail)

                #=> Materialize the path...
                filename = self.args[pattern]['filename']
                filename = self.config.get_file(filename,
                                                create_dir=True,
                                                extra={
                                                    'frame_name': f
                                                })
                # Collect all column information
                extra[f] = {
                    'columns': self.collapse_columns(detail),
                    'notes': self.collapse_notes(detail),
                    'descriptions': self.collapse_descriptions(detail),
                    'overrides': overrides
                }

                # Which dataframe
                df = detail['df']

                # Get the
                frametype = detail['frametype']

                # Order the dataframe if it is needed
                sortcols = self.args[pattern]['sort']
                if len(sortcols) > 0:
                    df = framecls.sort_values(df,
                                           sortcols,
                                           ascending=False)
                params = self.args[pattern].get('params',{})

                # Should I be writing this csv?
                save = params.get('save', True)
                save = overrides.get('save', save)

                if not save:
                    skipped.append(f)

                write_input[f] = {
                    'save': save,
                    'frametype': frametype,
                    'pattern': pattern,
                    'df': df,
                    'filename': filename,
                    'params': params,
                }

                args_input[f] = copy.copy(self.args[pattern])
                args_input[f]['filename'] = filename

        if len(skipped) > 0:
            logger.warning("Not saving {} tables".format(len(skipped)),
                           extra={
                               'transform': self.name,
                               'data': skipped
                           })

        # => Write output details
        framecls.write(args_input, write_input)

        for name in write_input:

            detail = write_input[name]

            # => Insert columns and tags
            pattern = detail['pattern']

            #
            detail['params']['tags'] = self.args[pattern]['tags']

            # Incorporate columns, notes and description
            additional_params = extra[name]
            overrides = additional_params.pop('overrides', {})

            detail['params'].update(additional_params)

            # Insert any overrides provided in the state
            if 'rows' in overrides:
                detail['params']['components'][0]['rows'] = overrides['rows']

            detail['params'] = [
                detail['params'],
                {
                    "type": "lineage",
                    "transform": self.name,
                    "dependencies": [
                        {
                            "type": "dataframe",
                            "nature": "input",
                            "objects": [name]
                        },
                        {
                            "type": "file",
                            "nature": "output",
                            "objects": [detail['filename']]
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

    def validate_results(self, what, state):
        pass

provider = TableSink
