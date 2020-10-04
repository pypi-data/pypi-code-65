# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tk_oddbox']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tk-oddbox',
    'version': '0.0.4',
    'description': 'Odd tkinter utilities, including image menu button',
    'long_description': None,
    'author': 'Andrew Allaire',
    'author_email': 'andrew.allaire@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
