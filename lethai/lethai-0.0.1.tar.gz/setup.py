# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lethai']

package_data = \
{'': ['*'], 'lethai': ['public/*']}

install_requires = \
['requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'lethai',
    'version': '0.0.1',
    'description': 'Lethical AI python library.',
    'long_description': None,
    'author': 'Amanl04',
    'author_email': 'amanlodha423@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
