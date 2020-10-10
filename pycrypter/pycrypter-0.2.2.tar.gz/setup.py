# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['pycrypter']
setup_kwargs = {
    'name': 'pycrypter',
    'version': '0.2.2',
    'description': '',
    'long_description': None,
    'author': 'Bekhs',
    'author_email': 'mypswset@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
