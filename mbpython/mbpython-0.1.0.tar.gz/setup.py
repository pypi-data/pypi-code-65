# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mbpython']

package_data = \
{'': ['*']}

install_requires = \
['pywin32>=228,<229']

setup_kwargs = {
    'name': 'mbpython',
    'version': '0.1.0',
    'description': 'miniblink binding for python',
    'long_description': None,
    'author': 'lochen',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
