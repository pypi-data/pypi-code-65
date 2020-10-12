# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gtfs_map_matcher']

package_data = \
{'': ['*'], 'gtfs_map_matcher': ['data/*']}

install_requires = \
['loguru>=0.5.3,<0.6.0',
 'pandas>=1.1.3,<2.0.0',
 'polyline>=1.4.0,<2.0.0',
 'requests-futures>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'gtfs-map-matcher',
    'version': '3.0.0',
    'description': 'A Python 3.8+ library to mshapes to Open Street Map roads',
    'long_description': None,
    'author': 'Alex Raichev',
    'author_email': 'araichev@mrcagney.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
