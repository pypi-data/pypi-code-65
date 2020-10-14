# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['odbc_niceties']

package_data = \
{'': ['*']}

install_requires = \
['cytoolz', 'pyodbc', 'tabulate']

setup_kwargs = {
    'name': 'odbc-niceties',
    'version': '0.2.0',
    'description': 'Some ODBC nice things.',
    'long_description': None,
    'author': 'joefromct',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
