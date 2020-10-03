# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sndslib']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['snds = sndslib.snds:main']}

setup_kwargs = {
    'name': 'sndslib',
    'version': '0.1.0',
    'description': 'Process and verify data from SNDS easily',
    'long_description': None,
    'author': 'undersfx',
    'author_email': 'undersoft.corp@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
