###############################################################################
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
###############################################################################
"""
onnxruntime_tools
this package includes transformers model optimization tools
"""
__version__ = "1.5.2"
__git_version__ = "186f0668b0ef5557db1827f90e3ad777265afd1e"
__author__ = "Microsoft Corporation"
__producer__ = "onnxruntime_tools"

import os
import sys
import types

from . import transformers

_transformers_path = os.path.join(os.path.dirname(__file__), 'transformers')
sys.path.append(_transformers_path)

from .transformers import optimizer  # noqa

sys.modules[__name__ + '.optimizer'] = types.ModuleType('optimizer')
