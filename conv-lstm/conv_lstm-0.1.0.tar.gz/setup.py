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
    'version': '0.1.0',
    'description': 'A PyTorch implementation for convolutional LSTM',
    'long_description': None,
    'author': 'Andrea Palazzi',
    'author_email': 'andrea.palazzi@unimore.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
