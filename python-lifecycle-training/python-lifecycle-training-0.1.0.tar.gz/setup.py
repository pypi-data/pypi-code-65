# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['python_lifecycle_training', 'python_lifecycle_training.calculator']

package_data = \
{'': ['*']}

install_requires = \
['dynaconf>=3.1.1,<4.0.0', 'fire>=0.3.1,<0.4.0', 'loguru>=0.5.3,<0.6.0']

entry_points = \
{'console_scripts': ['calc = python_lifecycle_training.calculator.cli:main']}

setup_kwargs = {
    'name': 'python-lifecycle-training',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Shashanka Prajapati',
    'author_email': 'shashanka@fusemachines.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
