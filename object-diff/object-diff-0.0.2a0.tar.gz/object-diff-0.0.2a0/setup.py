# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['object_diff']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'object-diff',
    'version': '0.0.2a0',
    'description': 'Library for diffing data structures of built-in types',
    'long_description': '# object-diff\n\nA Python library to diff built-in collection objects.',
    'author': 'Rolandas Valteris',
    'author_email': 'rolandas.valteris@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/ro/object-diff',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
