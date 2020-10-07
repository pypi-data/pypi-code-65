#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interpolate It widget controller class implementation
"""

from __future__ import print_function, division, absolute_import

import os

import tpDcc as tp
from tpDcc.libs.python import jsonio

from tpRigToolkit.tools.interpolateit.widgets import interpolator

LOGGER = tp.LogsMgr().get_logger('tpRigToolkit-tools-interpolateit')


class InterpolateItController(object):
    def __init__(self, client, model):
        super(InterpolateItController, self).__init__()

        self._client = client
        self._model = model

    @property
    def client(self):
        return self._client

    @property
    def model(self):
        return self._model

    def add_interpolator_widget(self, close_button_visible=True, title=None, items=None):
        interpolator_widget = interpolator.InterpolatorWidget(client=self._client)
        interpolator_widget.close_button_visible(close_button_visible)
        if title:
            interpolator_widget.model.title = title
        if items and isinstance(items, dict):
            interpolator_widget.model.items = items
        self._model.interpolator_widgets.append(interpolator_widget)
        self._model.addInterpolatorWidget.emit(interpolator_widget)

    def remove_interpolator_widget(self, interpolator_widget):
        self._model.interpolator_widgets.remove(interpolator_widget)
        self._model.removeInterpolatorWidget.emit(interpolator_widget)

    def save_data(self, file_path=None):
        interpolator_widgets = self._model.interpolator_widgets
        if not interpolator_widgets:
            return False

        data_to_store = list()
        for interpolator_widget in interpolator_widgets:
            interpolator_data = {
                'title': interpolator_widget.model.title,
                'data': interpolator_widget.model.items
            }
            data_to_store.append(interpolator_data)
        if not data_to_store:
            LOGGER.warning('No data to store')
            return False

        if not file_path or not os.path.isdir(file_path):
            file_path = tp.Dcc.save_file_dialog('Save File', pattern='*.json')
        if not file_path:
            return False

        valid = jsonio.write_to_file(data_to_store, file_path)
        if not valid:
            LOGGER.error('Error while saving JSON file ...')
            return False

        return True

    def load_data(self, file_path=None):
        if not file_path or not os.path.isfile(file_path):
            file_path = tp.Dcc.select_file_dialog('Open File', pattern='*.json')
        if not file_path or not os.path.isfile(file_path):
            return False

        data = jsonio.read_file(file_path)
        if not data:
            LOGGER.warning('Impossible to read data from {}'.format(file_path))
            return False

        self._model.prepareLoad.emit()

        for i, interpolator_data in enumerate(data):
            title = interpolator_data.get('title', None)
            data = interpolator_data.get('data', None)
            close_button_visible = False if i == 0 else True
            self.add_interpolator_widget(close_button_visible=close_button_visible, title=title, items=data)
