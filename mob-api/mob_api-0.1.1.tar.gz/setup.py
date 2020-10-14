# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mob_api']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6,<3.7',
 'pydes>=2,<3',
 'requests>=2.24,<2.25',
 'structlog>=20,<21']

setup_kwargs = {
    'name': 'mob-api',
    'version': '0.1.1',
    'description': 'mob api used by QiYuTech',
    'long_description': None,
    'author': 'dev',
    'author_email': 'dev@qiyutech.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
