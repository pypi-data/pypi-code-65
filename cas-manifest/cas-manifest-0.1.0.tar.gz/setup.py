# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cas_manifest']

package_data = \
{'': ['*']}

install_requires = \
['hashfs>=0.7.2,<0.8.0', 'pydantic>=1.6.1,<2.0.0']

setup_kwargs = {
    'name': 'cas-manifest',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Dan Frank',
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
