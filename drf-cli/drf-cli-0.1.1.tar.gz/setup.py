# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drf_cli']

package_data = \
{'': ['*']}

install_requires = \
['cookiecutter>=1.7.2,<2.0.0', 'pyyaml>=5.3.1,<6.0.0', 'typer>=0.2.1,<0.3.0']

entry_points = \
{'console_scripts': ['drf = drf_cli.app:app']}

setup_kwargs = {
    'name': 'drf-cli',
    'version': '0.1.1',
    'description': 'Tool for creating DRF projects',
    'long_description': None,
    'author': 'Patrick Rodrigues',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
