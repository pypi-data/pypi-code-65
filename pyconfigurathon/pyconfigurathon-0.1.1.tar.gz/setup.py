# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyconfigurathon']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyconfigurathon',
    'version': '0.1.1',
    'description': 'Simple python package to use a json file as a configuration file',
    'long_description': '#   PyConfigurathon\n\nA python package for making it easy to use configuration files for your python applications',
    'author': 'JermaineDavy',
    'author_email': None,
    'maintainer': 'Jermaine Davy',
    'maintainer_email': None,
    'url': 'https://github.com/JermaineDavy/pyconfigurathon',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8.2,<4.0.0',
}


setup(**setup_kwargs)
