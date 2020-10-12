# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ckan_crawler']

package_data = \
{'': ['*']}

install_requires = \
['git-filter-repo>=2.28.0,<3.0.0',
 'requests>=2.24.0,<3.0.0',
 'toml>=0.10.1,<0.11.0']

entry_points = \
{'console_scripts': ['ckan_crawler = ckan_crawler.main:main']}

setup_kwargs = {
    'name': 'ckan-crawler',
    'version': '0.1.10',
    'description': '',
    'long_description': None,
    'author': 'Lucas Bellomo',
    'author_email': 'lbellomo@gmail.com',
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
