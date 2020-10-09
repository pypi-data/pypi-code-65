# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ticktok']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'ticktok',
    'version': '0.1.0',
    'description': 'Official Python client for Ticktok.io',
    'long_description': None,
    'author': 'elis',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
