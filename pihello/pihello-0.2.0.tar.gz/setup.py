# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pihello']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pihello',
    'version': '0.2.0',
    'description': 'Highly configurable and scriptable Pi-hole statistics.',
    'long_description': None,
    'author': 'pavelgar',
    'author_email': 'pavel.garmuyev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
