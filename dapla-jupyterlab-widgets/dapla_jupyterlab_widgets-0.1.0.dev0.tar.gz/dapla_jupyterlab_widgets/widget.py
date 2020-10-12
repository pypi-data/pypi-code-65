#!/usr/bin/env python
# coding: utf-8

# Distributed under the terms of the Modified BSD License.

"""
This python class is used to retrieve data about the active notebook.
"""

from ipywidgets import DOMWidget
from traitlets import Unicode
from ._frontend import module_name, module_version


class ActiveNotebook(DOMWidget):
    """TODO: Add docstring here
    """
    _model_name = Unicode('ActiveNotebookModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('ActiveNotebookView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    title = Unicode('', help='The title (filename) of the active notebook').tag(sync=True)
