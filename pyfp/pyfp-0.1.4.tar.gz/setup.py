# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyfp']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyfp',
    'version': '0.1.4',
    'description': '',
    'long_description': None,
    'author': 'Brett Kolodny',
    'author_email': 'brettkolodny@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
