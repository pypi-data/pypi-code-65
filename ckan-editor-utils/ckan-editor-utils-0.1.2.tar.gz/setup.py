# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ckan_editor_utils']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.15.16,<2.0.0', 'requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'ckan-editor-utils',
    'version': '0.1.2',
    'description': 'Utilities for editing CKAN using its API.',
    'long_description': None,
    'author': 'Eric McCowan',
    'author_email': 'eric.mccowan@servian.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
