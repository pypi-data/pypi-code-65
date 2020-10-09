# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drf_firebase_token_auth']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'drf-firebase-token-auth',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Ron Heimann',
    'author_email': 'ron.heimann@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
