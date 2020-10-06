# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiacd', 'aiacd.tests']

package_data = \
{'': ['*']}

install_requires = \
['PySimpleGui>=4.29.0,<5.0.0',
 'openpyxl>=3.0.5,<4.0.0',
 'pandas>=1.1.2,<2.0.0',
 'sortedcollections>=1.2.1,<2.0.0']

setup_kwargs = {
    'name': 'aiacd',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'mjaquier',
    'author_email': 'mjaquier@mjaquier.xyz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
