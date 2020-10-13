# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simplemonads']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'simplemonads',
    'version': '1.0.0',
    'description': 'Simple Monads for Python. Use Just to end checking for None, Success to end unhandled exceptions, and Reader for dependency injection at runtime.',
    'long_description': None,
    'author': 'Stephen Daves',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3,<4',
}


setup(**setup_kwargs)
