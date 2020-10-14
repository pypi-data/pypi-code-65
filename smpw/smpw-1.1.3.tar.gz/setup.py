# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['smpw']
setup_kwargs = {
    'name': 'smpw',
    'version': '1.1.3',
    'description': 'hi my name Azarov Nick and i programist modile',
    'long_description': None,
    'author': 'John Smith',
    'author_email': 'azarovnick@bk.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
