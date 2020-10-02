# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['search_repo']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6.2,<4.0.0']

entry_points = \
{'console_scripts': ['search_repo = search_repo:main']}

setup_kwargs = {
    'name': 'search-repo',
    'version': '0.1.0',
    'description': 'Search for a github repo',
    'long_description': None,
    'author': 'Tomer Keren',
    'author_email': 'tomer.keren.dev@gmail.com',
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
