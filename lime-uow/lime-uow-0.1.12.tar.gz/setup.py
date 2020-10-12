# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lime_uow']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.3.19,<2.0.0']

setup_kwargs = {
    'name': 'lime-uow',
    'version': '0.1.12',
    'description': 'Framework to support the Unit-of-Work pattern',
    'long_description': None,
    'author': 'Mark Stefanovic',
    'author_email': 'markstefanovic@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MarkStefanovic/lime-uow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
