# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rfcpy', 'rfcpy.helpers']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0', 'peewee>=3.13.3,<4.0.0', 'requests>=2.24.0,<3.0.0']

entry_points = \
{'console_scripts': ['rfc = rfcpy.rfc:main']}

setup_kwargs = {
    'name': 'rfc.py',
    'version': '2020.10.1',
    'description': "A simple python client that offers users the ability to search for, read and bookmark RFC's from the Internet Engineering Task Force whilst offline.",
    'long_description': None,
    'author': 'danielmichaels',
    'author_email': 'dans.address@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
