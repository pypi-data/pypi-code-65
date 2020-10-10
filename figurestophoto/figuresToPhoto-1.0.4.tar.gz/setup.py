# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['figurestophoto']
setup_kwargs = {
    'name': 'figurestophoto',
    'version': '1.0.4',
    'description': 'EN: This module is needed to quickly draw shapes! First, install Pillow! RU: Этот модуль нужен, чтобы быстро рисовать фигуры! Для начала установите Pillow!',
    'long_description': None,
    'author': 'RealGames70',
    'author_email': '69468716+RealGames70@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
