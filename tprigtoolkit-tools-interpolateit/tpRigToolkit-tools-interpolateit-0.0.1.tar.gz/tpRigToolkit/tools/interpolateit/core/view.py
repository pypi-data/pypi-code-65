#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interpolate It widget view class implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, buttons


class InterpolateItView(base.BaseWidget, object):
    def __init__(self, model, controller, parent=None):

        self._model = model
        self._controller = controller

        super(InterpolateItView, self).__init__(parent=parent)

        # Add base interpolator widget (which cannot be closed)
        self._controller.add_interpolator_widget(close_button_visible=False)

    def get_main_layout(self):
        main_layout = layouts.VerticalLayout(spacing=2, margins=(2, 2, 2, 2))

        return main_layout

    def ui(self):
        super(InterpolateItView, self).ui()

        central_layout = layouts.VerticalLayout(spacing=0, margins=(0, 0, 0, 0))
        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        central_widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setFocusPolicy(Qt.NoFocus)
        self.main_layout.addWidget(scroll)
        scroll.setWidget(central_widget)

        self._interpolator_layout = layouts.VerticalLayout(spacing=0, margins=(0, 0, 0, 0))
        self._interpolator_layout.setAlignment(Qt.AlignTop)

        button_layout = layouts.HorizontalLayout(spacing=2, margins=(0, 0, 0, 0))
        self._load_btn = buttons.BaseButton('Load', parent=self)
        self._save_btn = buttons.BaseButton('Save', parent=self)
        self._add_btn = buttons.BaseButton('New', parent=self)
        button_layout.addWidget(self._save_btn)
        button_layout.addWidget(self._load_btn)
        button_layout.addStretch()
        button_layout.addWidget(self._add_btn)

        central_layout.addLayout(self._interpolator_layout)

        self.main_layout.addLayout(button_layout)

        # new_widget = interpolator.InterpolatorWidget(client=self._controller.client, parent=self)
        # new_widget.close_button_visible(False)
        # self._interpolator_layout.addWidget(new_widget)
        # self._model.interpolator_widgets.append(new_widget)

    def setup_signals(self):
        self._add_btn.clicked.connect(self._controller.add_interpolator_widget)
        self._save_btn.clicked.connect(self._controller.save_data)
        self._load_btn.clicked.connect(self._controller.load_data)

        self._model.addInterpolatorWidget.connect(self._on_add_interpolator_widget)
        self._model.removeInterpolatorWidget.connect(self._on_remove_interpolator_widget)
        self._model.prepareLoad.connect(self._on_prepare_load)

    def clear_all_widgets(self):
        interpolator_widgets = self._model.interpolator_widgets
        if not interpolator_widgets:
            return
        for interpolator_widget in interpolator_widgets:
            self._controller.remove_interpolator_widget(interpolator_widget)

    def _on_add_interpolator_widget(self, interpolator_widget):
        self._interpolator_layout.addWidget(interpolator_widget)
        interpolator_widget.closeWidget.connect(self._controller.remove_interpolator_widget)
        interpolator_widget.setFixedHeight(0)
        interpolator_widget.animate_expand(True)

    def _on_remove_interpolator_widget(self, interpolator_widget):
        interpolator_widget.deleteWidget.connect(self._on_delete)
        interpolator_widget.animate_expand(False)

    def _on_delete(self, interpolator_widget):
        self._interpolator_layout.removeWidget(interpolator_widget)
        interpolator_widget.clear_animation()
        interpolator_widget.deleteLater()

    def _on_prepare_load(self):
        self.clear_all_widgets()
