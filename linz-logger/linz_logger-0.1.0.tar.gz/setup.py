# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['linz_logger']

package_data = \
{'': ['*']}

install_requires = \
['structlog>=20.1.0,<21.0.0']

setup_kwargs = {
    'name': 'linz-logger',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Blayne',
    'author_email': 'bchard@linz.govt.nz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
