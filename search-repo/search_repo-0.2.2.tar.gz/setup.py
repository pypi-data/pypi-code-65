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
    'version': '0.2.2',
    'description': 'Search for a github repo',
    'long_description': '# Search Repo \n## Finds the most relevant repo in the command line\n[![PyPI version](https://badge.fury.io/py/search-repo.svg)](https://badge.fury.io/py/search-repo) [![Downloads](https://pepy.tech/badge/search-repo)](https://pepy.tech/project/search-repo) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n---\n\n### Installation \n```sh\npip install search_repo\n```\n\n### Usage\n```bash\n# Returns the link to clone the repo\n$ search_repo cppcoro\ngit@github.com:lewissbaker/cppcoro\n\n# Easily used with git clone!\n$ git clone $(search_repo cppcoro)\n```\n',
    'author': 'Tomer Keren',
    'author_email': 'tomer.keren.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Tadaboody/search_repo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
