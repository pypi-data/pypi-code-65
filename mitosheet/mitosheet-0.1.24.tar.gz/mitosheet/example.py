#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""
import json
import analytics
import pandas as pd
from ipywidgets import DOMWidget
from traitlets import Unicode, List

from ._frontend import module_name, module_version
from .transpile import transpile
from .errors import EditError
from .utils import empty_column_python_code, get_invalid_headers
from mitosheet.widget_state_container import WidgetStateContainer

from mitosheet.mito_analytics import analytics, static_user_id

class MitoWidget(DOMWidget):
    """TODO: Add docstring here
    """
    _model_name = Unicode('ExampleModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('ExampleView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    value = Unicode('Hello World').tag(sync=True)
    sheet_json = Unicode('').tag(sync=True)
    code_json = Unicode('').tag(sync=True)
    df_name = Unicode('').tag(sync=True)
    user_id = Unicode(static_user_id).tag(sync=True)
    column_spreadsheet_code_json = Unicode('').tag(sync=True)
    edit_event_list = List()

    def __init__(self, *args, **kwargs):
        # Call the DOMWidget constructor to set up the widget properly
        super(MitoWidget, self).__init__(*args, **kwargs)
        self.analysis_name = kwargs['analysis_name'] if 'analysis_name' in kwargs else ''
        self.df = kwargs['df'] if kwargs['df'] is not None else pd.DataFrame() # make a 

        # We restrict keys early, to alert users if they use headers we don't support
        invalid_column_headers = get_invalid_headers(self.df)
        invalid_column_headers_str = ', '.join([str(ch) for ch in invalid_column_headers])
        if len(invalid_column_headers) != 0:
            raise ValueError(f'All headers in the dataframe must contain at least one letter and no symbols other than numbers, - and _. Invalid headers: {invalid_column_headers_str}')

        # Set up starting shared state variables
        self.sheet_json = df_to_json(self.df)
        self.code_json = json.dumps({"code": "0"})
        self.df_name = ''
        self.column_spreadsheet_code_json = json.dumps({key: '' for key in self.df.keys()})

        # Set up the state container to hold private widget state
        self.widget_state_container = WidgetStateContainer(self.df)

        # Set up message handler
        self.on_msg(self.receive_message)
        
    def send(self, msg):
        """
        We overload the DOMWidget's send function, so that 
        we log all outgoing messages
        """
        # Send the message though the DOMWidget's send function
        super().send(msg)
        # Log the message as sent
        analytics.track(self.user_id, 'py_sent_msg_log_event', {'event': msg})

    def saturate(self, event):
        """
        Saturation is when the server fills in information that
        is missing from the event client-side. This is for consistency
        and because the client may not have easy access to the info
        all the time.
        """
        if event['event'] == 'edit_event':
            if event['type'] == 'cell_edit':
                address = event['address']
                event['old_formula'] = self.widget_state_container.column_spreadsheet_code[address]

    def handle_edit_event(self, event):
        """
        Handles an edit_event. Per the spec, an edit_event
        updates both the sheet and the codeblock, and as such
        the sheet is re-evaluated and the code for the codeblock
        is re-transpiled.

        Useful for any event that changes the state of both the sheet
        and the codeblock!
        """
        # First, we send this new edit to the evaluator
        analytics.track(self.user_id, 'evaluator_started_log_event')
        self.widget_state_container.handle_edit_event(event)
        analytics.track(self.user_id, 'evaluator_finished_log_event')

        # Then, we run the transpiler on the new state
        analytics.track(self.user_id, 'transpiler_started_log_event')
        code_container = transpile(self.widget_state_container)
        analytics.track(self.user_id, 'transpiler_finished_log_event')

        # We update the state variables for the sheet
        self.column_spreadsheet_code_json = json.dumps(self.widget_state_container.column_spreadsheet_code)
        self.sheet_json = df_to_json(self.widget_state_container.df)
        
        # And update the state variable for the code block
        self.code_json = json.dumps(code_container)

        # Tell the front-end to render the new sheet and new code
        self.send({"event": "update_sheet"})
        self.send({"event": "update_code"})

    def handle_sheet_update_event(self, event):
        """
        Handles a sheet_update_event. Per the spec, an sheet_update_event
        updates just the sheet and not the codeblock. 

        This is useful for events that _change_ the currently selected
        JupyterLab cell; as such, updating this cell would be incorrect,
        as it is not the correct codeblock to update!
        """
        # Handle the update event
        self.widget_state_container.handle_sheet_update_event(event)
        # We update the state variables for the sheet
        self.column_spreadsheet_code_json = json.dumps(self.widget_state_container.column_spreadsheet_code)
        self.sheet_json = df_to_json(self.widget_state_container.df)
        # Tell the front-end to render the new sheet and new code
        self.send({"event": "update_sheet"})

    def receive_message(self, widget, content, buffers=None):
        """
        Handles all incoming messages from the JS widget. There are two main
        types of events:

        1. edit_event: any event that updates the state of the sheet and the
        code block at once. Leads to reevaluation, and a re-transpile.

        2. sheet_update_event: updates some piece of the sheet state, but does
        not update the transpiled code or the codeblock. This is useful for some 
        edits that make new cells, and so change which code cell is currently 
        highlighted - meaning an update to it would update the wrong cell!

        See function doc strings for more information.
        """
        # First, we saturate the event
        event = content
        self.saturate(event)

        # Then log that we got this message
        analytics.track(self.user_id, 'py_recv_msg_log_event', {'event': event})

        try:
            if event['event'] == 'edit_event':
                self.handle_edit_event(event)
            if event['event'] == 'sheet_update_event':
                self.handle_sheet_update_event(event)
        except EditError as e:
            # If we hit an error during editing, log that it has occured
            analytics.track(
                self.user_id, 
                f'{e.type_}_log_event', 
                {'header': e.header, 'to_fix': e.to_fix}
            )
            # Report it to the user, and then return
            self.send({
                'event': 'edit_error',
                'type': e.type_,
                'header': e.header,
                'to_fix': e.to_fix
            })


def sheet(df: pd.DataFrame) -> MitoWidget:
    return MitoWidget(df=df)

def df_to_json(df=None):
    if df is None:
        return '{}'
    json_obj = json.loads(df.to_json(orient="split"))
    # Then, we go through and find all the null values (which are infinities),
    # and set them to undefined.
    for d in json_obj['data']:
        for idx, e in enumerate(d):
            if e is None:
                d[idx] = 'undefined'
    return json.dumps(json_obj)

