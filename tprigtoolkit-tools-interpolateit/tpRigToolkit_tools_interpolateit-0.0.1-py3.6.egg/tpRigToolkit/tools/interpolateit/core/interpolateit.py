#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool to store/blend interpolate states of objects
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import importlib

import tpDcc as tp
from tpDcc.core import tool
from tpDcc.libs.qt.widgets import toolset

from tpRigToolkit.tools.interpolateit.core import interpolateitclient

# Defines ID of the tool
TOOL_ID = 'tpRigToolkit-tools-interpolateit'


class InterpolateItTool(tool.DccTool, object):
    def __init__(self, *args, **kwargs):
        super(InterpolateItTool, self).__init__(*args, **kwargs)

    @classmethod
    def config_dict(cls, file_name=None):
        base_tool_config = tool.DccTool.config_dict(file_name=file_name)
        tool_config = {
            'name': 'Interpolate It',
            'id': TOOL_ID,
            'supported_dccs': {'maya': ['2017', '2018', '2019', '2020']},
            'logo': 'jointorient',
            'icon': 'jointorient',
            'tooltip': 'Tool to store/blend interpolate states of objects',
            'tags': ['tpRigToolkit', 'interpolate', 'animation', 'state', 'pose'],
            'logger_dir': os.path.join(os.path.expanduser('~'), 'tpRigToolkit', 'logs', 'tools'),
            'logger_level': 'INFO',
            'is_checkable': False,
            'is_checked': False,
            'menu_ui': {'label': 'Interpolate It', 'load_on_startup': False, 'color': '', 'background_color': ''},
            'size': [425, 600]
        }
        base_tool_config.update(tool_config)

        return base_tool_config

    def launch(self, *args, **kwargs):
        return self.launch_frameless(*args, **kwargs)


class InterpolateItToolset(toolset.ToolsetWidget, object):
    ID = TOOL_ID

    def __init__(self, *args, **kwargs):
        super(InterpolateItToolset, self).__init__(*args, **kwargs)

    def setup_client(self):

        self._client = interpolateitclient.InterpolateItClient()
        self._client.signals.dccDisconnected.connect(self._on_dcc_disconnected)

        if not tp.is_standalone():
            dcc_mod_name = '{}.dccs.{}.interpolateitserver'.format(TOOL_ID.replace('-', '.'), tp.Dcc.get_name())
            try:
                mod = importlib.import_module(dcc_mod_name)
                if hasattr(mod, 'InterpolateItServer'):
                    server = mod.InterpolateItServer(self, client=self._client, update_paths=False)
                    self._client.set_server(server)
                    self._update_client()
            except Exception as exc:
                tp.logger.warning(
                    'Impossible to launch Interpolate It server! Error while importing: {} >> {}'.format(
                        dcc_mod_name, exc))
                return
        else:
            self._update_client()

    def contents(self):

        from tpRigToolkit.tools.interpolateit.core import model, view, controller

        interpolate_it_model = model.InterpolateItModel()
        interpolate_it_controller = controller.InterpolateItController(client=self._client, model=interpolate_it_model)
        interpolate_it_view = view.InterpolateItView(
            model=interpolate_it_model, controller=interpolate_it_controller, parent=self)

        return [interpolate_it_view]
