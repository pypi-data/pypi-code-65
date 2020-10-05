# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crplog']

package_data = \
{'': ['*']}

install_requires = \
['aihelper>=0.2.4,<0.3.0',
 'aitkhelp>=0.1.0,<0.2.0',
 'pandas>=1.1.2,<2.0.0',
 'xlrd>=1.2.0,<2.0.0']

setup_kwargs = {
    'name': 'crplog',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'mjaquier',
    'author_email': 't',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
