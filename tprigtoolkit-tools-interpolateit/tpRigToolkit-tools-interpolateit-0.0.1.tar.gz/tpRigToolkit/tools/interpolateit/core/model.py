#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interpolate It widget model class implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *


class InterpolateItModel(QObject, object):

    addInterpolatorWidget = Signal(object)
    removeInterpolatorWidget = Signal(object)
    prepareLoad = Signal()

    def __init__(self):
        super(InterpolateItModel, self).__init__()

        self._interpolator_widgets = list()

    @property
    def interpolator_widgets(self):
        return self._interpolator_widgets
