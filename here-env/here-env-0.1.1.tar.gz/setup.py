# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['here_env']
install_requires = \
['click>=7.1.2,<8.0.0']

entry_points = \
{'console_scripts': ['here-env = here_env:cli']}

setup_kwargs = {
    'name': 'here-env',
    'version': '0.1.1',
    'description': 'Small helper to create and active virtuel environments.',
    'long_description': None,
    'author': 'Simon Westphahl',
    'author_email': 'simon@westphahl.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
