# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['garnett']

package_data = \
{'': ['*']}

install_requires = \
['django>3.0']

setup_kwargs = {
    'name': 'django-garnett',
    'version': '0.0.1',
    'description': 'Simple translatable Django fields',
    'long_description': None,
    'author': 'Aristotle Metadata Enterprises',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
