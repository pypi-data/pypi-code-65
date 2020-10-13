# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['composable']

package_data = \
{'': ['*']}

install_requires = \
['python-forge>=18.6,<19.0', 'toolz>=0.11.1,<0.12.0']

setup_kwargs = {
    'name': 'composable',
    'version': '0.2.2',
    'description': 'Callable functions that be composed/piped using >> and <<',
    'long_description': None,
    'author': 'Todd Iverson',
    'author_email': 'tiverson@winona.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
