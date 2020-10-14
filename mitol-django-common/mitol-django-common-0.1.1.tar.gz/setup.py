# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mitol', 'mitol.common']

package_data = \
{'': ['*']}

install_requires = \
['Django>=2.2.12,<3.0.0',
 'psycopg2-binary>=2.8.3,<3.0.0',
 'requests>=2.20.0,<3.0.0']

setup_kwargs = {
    'name': 'mitol-django-common',
    'version': '0.1.1',
    'description': 'MIT Open Learning django app extensions for common utilities',
    'long_description': None,
    'author': 'MIT Office of Open Learning',
    'author_email': 'mitx-devops@mit.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<3.9',
}


setup(**setup_kwargs)
