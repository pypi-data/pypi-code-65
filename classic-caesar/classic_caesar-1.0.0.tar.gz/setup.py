# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['classic_caesar']
setup_kwargs = {
    'name': 'classic-caesar',
    'version': '1.0.0',
    'description': 'Модуль для зашифровывания файлов. | File encryption module.',
    'long_description': None,
    'author': 'F_social',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
