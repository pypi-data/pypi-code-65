# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tolha']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.5.3,<0.6.0',
 'playwright>=0.142.3,<0.143.0',
 'python-decouple>=3.3,<4.0']

setup_kwargs = {
    'name': 'tolha',
    'version': '0.1.0',
    'description': 'Unofficial Library to access your my ais data',
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
