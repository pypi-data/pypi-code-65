# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['neuroio',
 'neuroio.api',
 'neuroio.api.entries',
 'neuroio.api.groups',
 'neuroio.api.notifications',
 'neuroio.api.persons',
 'neuroio.api.settings',
 'neuroio.api.sources',
 'neuroio.api.utility',
 'neuroio.iam',
 'neuroio.iam.auth',
 'neuroio.iam.spaces',
 'neuroio.iam.tokens',
 'neuroio.iam.whoami']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.16.1,<0.17.0']

setup_kwargs = {
    'name': 'neuroio',
    'version': '0.0.3',
    'description': 'A Python package for interacting with NeuroIO API',
    'long_description': 'neuroio-python\n_________________\n\n[![PyPI version](https://badge.fury.io/py/neuroio.svg)](http://badge.fury.io/py/neuroio)\n[![codecov](https://codecov.io/gh/neuroio/neuroio-python/branch/master/graph/badge.svg)](https://codecov.io/gh/neuroio/neuroio-python)\n[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.python.org/pypi/neuroio/)\n[![Downloads](https://pepy.tech/badge/neuroio)](https://pepy.tech/project/neuroio)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://timothycrosley.github.io/isort/)\n\n_________________\n\n[Read Latest Documentation](https://neuroio.github.io/neuroio-python/) - [Browse GitHub Code Repository](https://github.com/neuroio/neuroio-python/)\n_________________\n\n**neuroio-python** A Python package for interacting with NeuroIO API\n',
    'author': 'Lev Rubel',
    'author_email': 'l@datacorp.ee',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
