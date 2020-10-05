# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['loadbarpy']
setup_kwargs = {
    'name': 'loadbarpy',
    'version': '1.0.0',
    'description': 'Cool loadbar for your python programs. Usage: LoadPy(\\"nameofanimation\\").animate() Animation names: default, miniload, bigload',
    'long_description': None,
    'author': 'FreshHacks',
    'author_email': 'ddkkosta@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
