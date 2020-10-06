# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cobra_py']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cobra-py',
    'version': '0.0.1',
    'description': 'An 80s style Python runtime and development environment',
    'long_description': None,
    'author': 'Roberto Alsina',
    'author_email': 'roberto.alsina@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
