import os, copy
import numpy as np
from hashlib import sha256
from datetime import datetime
import logging

from enrichsdk import Source

logger = logging.getLogger("app")

class TableSource(Source):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "TableSource"

    def preload_clean_args(self, args):
        """
        Clean when the spec is loaded...
        """
        # Sanity check...
        assert isinstance(args, dict)

        for name, detail  in args.items():

            # Insert the frame into the args for backward
            # compatability.
            if (("type" in detail) and
                ("frametype" not in detail) and
                (detail['type'] == 'table')):
                detail['frametype'] = 'pandas'

            if (("frametype" not in detail) or
                (detail['frametype'] != 'pandas')):
                logger.error("Invalid configuration. Only pandas table source supported by this source transform",
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

            mapping = {
                'str': str,
                'float': np.float64,
                'float64': np.float64,
                'np.float64': np.float64,
                'np.int64': np.int64,
                'int': np.int64,
                'int64': np.int64,
                'datetime': datetime,
                'category': 'category'
            }

            #=> Materialize the path...
            detail['filename'] = self.config.get_file(detail['filename'])
            detail['root'] = self.config.enrich_data_dir
            params = detail['params']
            if 'dtype' in params:
                for attr in params['dtype']:
                    if params['dtype'][attr] in mapping:
                        params['dtype'][attr] = mapping[params['dtype'][attr]]
                    else:
                        params['dtype'][attr] = eval(params['dtype'][attr])

        return args

    def validate_args(self, what, state):

        assert isinstance(self.args, dict)
        for name, detail  in self.args.items():
            assert (('frametype' in detail) and (detail['frametype'] == 'pandas'))
            assert 'filename' in detail
            assert 'params' in detail

    def sample_inputs(self):

        frame = self.config.get_dataframe('pandas')
        args = self.args

        # Read 50 rows only...
        args = copy.deepcopy(self.args)
        for name in args:
            if 'params' not in args[name]:
                args[name]['params'] = {}
            args[name]['params']['nrows'] = 50

        # => Load the tables
        try:
            dfstates = frame.read(args, {})
        except:
            logger.exception("Error while loading the inputs")
            return []

        # => Generate the inputs for the caller...
        inputs = []
        for name in args:
            detail = dfstates[name]
            table = [list(frame.columns(detail['df']))] + \
                    frame.tolist(frame.head(detail['df'], 4))
            inputs.append({
                'name': name,
                'rows': frame.shape(detail['df'])[0],
                'columns': frame.shape(detail['df'])[1],
                'params': detail['params'],
                'table': table
            })

        return inputs

    def clean(self, state):
        """
        This is meant for subclass to do some additional processing.
        """
        pass

    def validate_results(self, what, state):
        pass

    def process(self, state):
        """
        Load file...
        """
        # Load all the dataframes. This will use the full enrich
        # deployment's beefed up read function.
        framecls = self.config.get_dataframe('pandas')
        dfstates = framecls.read(self.args, {})
        for dfname, dfstate in dfstates.items():

            # => Insert column description
            columns = dfstate['params']['columns']
            for c in columns:
                columns[c]['description'] = self.get_column_description(dfname, c)

            params = dfstate['params']
            if 'filename' in params:
                filename = params['filename']
            elif 'filename' in self.args.get(dfname,{}):
                filename = self.args[dfname]['filename']
            else:
                filename = "Unknown"

            detail = {
                'df': dfstate['df'],
                'transform': self.name,
                'frametype': 'pandas',
                'params': [
                    params,
                    {
                        "type": "lineage",
                        "transform": self.name,
                        "dependencies": [
                            {
                                "type": "file",
                                "nature": "input",
                                "objects": [filename]
                            }
                        ]
                    }
                ],
                'history': [
                    {
                        'transform': self.name,
                        'log': "Read data using {}".format(framecls.__class__.__name__)
                    }
                ]
            }
            try:
                state.update_frame(dfname, detail, create=True)
            except:
                logger.exception("Unable to store state",
                             extra=self.config.get_extra({
                                 'transform': self.name
                             }))
                raise Exception("Error while loading")

        # Clean the uploaded data...
        self.clean(state)


provider = TableSource
