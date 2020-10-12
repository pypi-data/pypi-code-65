# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iso_4217']

package_data = \
{'': ['*'], 'iso_4217': ['data/*']}

setup_kwargs = {
    'name': 'iso-4217',
    'version': '0.1.180829',
    'description': 'ISO 4217 currency code library',
    'long_description': None,
    'author': 'Igor Kozyrenko',
    'author_email': 'igor@ikseek.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
