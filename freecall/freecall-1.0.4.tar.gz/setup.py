# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['freecall']

package_data = \
{'': ['*']}

install_requires = \
['dill>=0.3.2,<0.4.0']

setup_kwargs = {
    'name': 'freecall',
    'version': '1.0.4',
    'description': '',
    'long_description': None,
    'author': 'Zenith',
    'author_email': 'z@zenith.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
