# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bomist_utils']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['bomist_cli = bomist_utils:cli']}

setup_kwargs = {
    'name': 'bomist-utils',
    'version': '0.1.0',
    'description': 'BOMIST Utilities',
    'long_description': None,
    'author': 'Mario Ribeiro',
    'author_email': 'mario@rasgo.cc',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
