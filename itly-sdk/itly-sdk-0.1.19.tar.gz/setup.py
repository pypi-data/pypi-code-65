# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['itly_sdk', 'itly_sdk.internal']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'itly-sdk',
    'version': '0.1.19',
    'description': 'Iteratively Analytics SDK',
    'long_description': '',
    'author': 'Iteratively',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
