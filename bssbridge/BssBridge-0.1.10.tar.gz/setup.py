# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bssbridge',
 'bssbridge.commands.dbf',
 'bssbridge.lib',
 'bssbridge.lib.ftp',
 'bssbridge.lib.pool']

package_data = \
{'': ['*']}

install_requires = \
['aioftp>=0.18.0,<0.19.0',
 'aiohttp>=3.5.4,<4.0.0',
 'asyncio>=3.4.3,<4.0.0',
 'bssapi-schemas>=0.1.0,<0.2.0',
 'cleo>=0.8.1,<0.9.0',
 'lz4>=3.1.0,<4.0.0',
 'orjson>=3.3.1,<4.0.0',
 'pydantic>=1.6.1,<2.0.0',
 'sentry-sdk>=0.17.8,<0.18.0']

entry_points = \
{'console_scripts': ['bb = bssbridge:main']}

setup_kwargs = {
    'name': 'bssbridge',
    'version': '0.1.10',
    'description': 'Робот доставки данных в систему BSS',
    'long_description': None,
    'author': 'Anton Rastyazhenko',
    'author_email': 'rastyazhenko.anton@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
