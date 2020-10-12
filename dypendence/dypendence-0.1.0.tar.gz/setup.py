# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dypendence']

package_data = \
{'': ['*']}

install_requires = \
['dynaconf>=3.1.2,<4.0.0']

setup_kwargs = {
    'name': 'dypendence',
    'version': '0.1.0',
    'description': 'Dependency Injection over Dynaconf',
    'long_description': None,
    'author': 'VaultVulp',
    'author_email': 'me@vaultvulp.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
