# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['composablesoup']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'composable>=0.2.0,<0.3.0',
 'python-forge>=18.6,<19.0']

setup_kwargs = {
    'name': 'composablesoup',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Todd Iverson',
    'author_email': 'tiverson@smumn.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
