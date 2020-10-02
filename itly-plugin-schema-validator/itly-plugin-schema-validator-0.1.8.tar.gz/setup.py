# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['itly_plugin_schema_validator']

package_data = \
{'': ['*']}

install_requires = \
['itly-sdk>=0.1.0,<0.2.0', 'jsonschema>=3.2.0,<4.0.0']

setup_kwargs = {
    'name': 'itly-plugin-schema-validator',
    'version': '0.1.8',
    'description': 'Iteratively Analytics SDK - Schema Validator Plugin',
    'long_description': '',
    'author': 'Iteratively',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
