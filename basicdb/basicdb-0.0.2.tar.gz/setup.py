# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['basicdb']

package_data = \
{'': ['*']}

install_requires = \
['msgpack>=1.0.0,<2.0.0',
 'objectstash>=0.1,<0.2',
 'sqlalchemy>=1.3.19,<2.0.0',
 'sqlalchemy_utils==0.36.7']

setup_kwargs = {
    'name': 'basicdb',
    'version': '0.0.2',
    'description': '',
    'long_description': None,
    'author': 'Ludwig Schmidt',
    'author_email': 'ludwigschmidt2@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
