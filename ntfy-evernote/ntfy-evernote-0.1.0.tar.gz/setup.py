# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ntfy_evernote']
install_requires = \
['evernote3>=1.25.14,<2.0.0', 'oauth2>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'ntfy-evernote',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Cologler',
    'author_email': 'skyoflw@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
