# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['conv_lstm']

package_data = \
{'': ['*']}

install_requires = \
['torch>=1.5.0']

setup_kwargs = {
    'name': 'conv-lstm',
    'version': '0.1.2',
    'description': 'A PyTorch implementation for convolutional LSTM',
    'long_description': '# [conv_lstm_pytorch](https://github.com/Jimexist/conv_lstm_pytorch)\n\n[![PyPI](https://img.shields.io/pypi/v/conv-lstm?style=flat-square)](https://pypi.org/project/conv-lstm)\n\nThis version is forked and adapted from https://github.com/ndrplz/ConvLSTM_pytorch.\n\nOriginal authors are:\n\n- https://github.com/ndrplz/ConvLSTM_pytorch\n- https://github.com/DavideA\n- https://github.com/rogertrullo/pytorch_convlstm\n\nPlease checkout the code itself and unit tests for details usage and examples.\n\n## Code style\n\nThis repo is managed by poetry, formatted by black, isort, and type checked by mypy.\n',
    'author': 'Andrea Palazzi',
    'author_email': 'andrea.palazzi@unimore.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Jimexist/conv_lstm_pytorch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
