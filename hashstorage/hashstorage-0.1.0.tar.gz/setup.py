# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hashstorage']

package_data = \
{'': ['*']}

install_requires = \
['Flask==1.1.1']

entry_points = \
{'console_scripts': ['hashstorage-cli = hashstorage.cli:main']}

setup_kwargs = {
    'name': 'hashstorage',
    'version': '0.1.0',
    'description': 'Implementation of Simple-HashStorage.',
    'long_description': None,
    'author': 'chike0905',
    'author_email': 'chike@sfc.wide.ad.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chike0905/simple-hashstorage',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
