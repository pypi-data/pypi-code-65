# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['jisx0402']
install_requires = \
['pydantic>=1.6.1,<2.0.0']

setup_kwargs = {
    'name': 'jisx0402',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'kitagawa-hr',
    'author_email': 'kitagawa@cancerscan.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
