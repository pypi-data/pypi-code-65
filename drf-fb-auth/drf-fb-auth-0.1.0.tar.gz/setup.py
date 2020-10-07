# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drf_fb_auth']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'drf-fb-auth',
    'version': '0.1.0',
    'description': 'Firebase Authentication for Django Rest Framework',
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
