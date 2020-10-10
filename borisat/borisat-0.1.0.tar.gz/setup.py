# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['borisat', 'borisat.apis', 'borisat.models', 'borisat.models.rd']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.5.3,<0.6.0',
 'pydantic>=1.6.1,<2.0.0',
 'stringcase>=1.2.0,<2.0.0',
 'zeep>=3.4.0,<4.0.0']

setup_kwargs = {
    'name': 'borisat',
    'version': '0.1.0',
    'description': 'a python library for retrieving company public data in thailand. It has its own public database for caching, so, it is really fast, smart, and save lot of time and energy.',
    'long_description': None,
    'author': 'Nutchanon Ninyawee',
    'author_email': 'nutchanon@codustry.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
