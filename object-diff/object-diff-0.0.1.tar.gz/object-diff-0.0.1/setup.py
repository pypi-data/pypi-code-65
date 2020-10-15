# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['object_diff']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'object-diff',
    'version': '0.0.1',
    'description': 'Library for diffing data structures of built-in types',
    'long_description': None,
    'author': 'Rolandas Valteris',
    'author_email': 'rolandas.valteris@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
