#!/usr/bin/env python
# coding: utf-8

# Distributed under the terms of the Modified BSD License.

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'nbextension/static',
        'dest': 'dapla_jupyterlab_widgets',
        'require': 'dapla_jupyterlab_widgets/extension'
    }]
