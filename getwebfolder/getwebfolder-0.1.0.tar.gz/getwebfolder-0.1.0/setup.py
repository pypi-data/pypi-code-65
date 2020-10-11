# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['getwebfolder']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.24.0,<3.0.0', 'ujson>=4.0.1,<5.0.0']

setup_kwargs = {
    'name': 'getwebfolder',
    'version': '0.1.0',
    'description': 'Get files and data from a given web folder (bare url)',
    'long_description': None,
    'author': 'skeptycal',
    'author_email': '26148512+skeptycal@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
