# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['onlconvert']
setup_kwargs = {
    'name': 'onlconvert',
    'version': '0.0.1',
    'description': 'Python conventor',
    'long_description': None,
    'author': 'onleew',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
