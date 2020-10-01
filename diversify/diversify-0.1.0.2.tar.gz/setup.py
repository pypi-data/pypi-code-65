# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['diversify', 'diversify.tf']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6.2,<4.0.0',
 'click>=7.1.2,<8.0.0',
 'colorama>=0.4.3,<0.5.0',
 'numpy>=1.19.2,<2.0.0',
 'pandas>=1.1.2,<2.0.0',
 'python-dotenv>=0.14.0,<0.15.0',
 'spotipy>=2.16.0,<3.0.0']

entry_points = \
{'console_scripts': ['diversify = diversify.main:diversify']}

setup_kwargs = {
    'name': 'diversify',
    'version': '0.1.0.2',
    'description': 'A small playlist generator for spotify',
    'long_description': None,
    'author': 'Eduardo Macedo',
    'author_email': 'eduzemacedo@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
