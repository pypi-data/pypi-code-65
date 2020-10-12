# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sqlalchemy_crud', 'sqlalchemy_crud.tests']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.3.19,<2.0.0']

setup_kwargs = {
    'name': 'sqlalchemy-crud',
    'version': '0.1.0b0',
    'description': 'Basic C.R.U.D for SQLAlchemy models',
    'long_description': None,
    'author': 'Clayton Black',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cblack34/sqlalchemy-crud',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
