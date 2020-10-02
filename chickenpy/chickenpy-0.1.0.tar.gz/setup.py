# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chickenpy']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1,<8.0']

entry_points = \
{'console_scripts': ['chickenpy = chickenpy.__main__:main']}

setup_kwargs = {
    'name': 'chickenpy',
    'version': '0.1.0',
    'description': 'A Python implementation of the Chicken esoteric programming language',
    'long_description': None,
    'author': 'kosayoda',
    'author_email': 'kieransiek@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kosayoda/chickenpy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
