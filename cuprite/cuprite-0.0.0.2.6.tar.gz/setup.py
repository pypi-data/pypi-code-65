# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['cuprite']
install_requires = \
['ujson>=3.2.0,<4.0.0']

setup_kwargs = {
    'name': 'cuprite',
    'version': '0.0.0.2.6',
    'description': '',
    'long_description': None,
    'author': 'Andrew',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
