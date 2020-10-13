# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['rrl']
install_requires = \
['redis>=3.5.3,<4.0.0']

setup_kwargs = {
    'name': 'rrl',
    'version': '0.2.2',
    'description': 'simple redis rate limiting',
    'long_description': None,
    'author': 'James Turk',
    'author_email': 'dev@jamesturk.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
