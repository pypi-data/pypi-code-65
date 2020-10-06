# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['w_parser']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'lxml>=4.5.2,<5.0.0',
 'requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'w-parser',
    'version': '0.3.0',
    'description': 'Parser for job search sites',
    'long_description': None,
    'author': 'dayonizeus',
    'author_email': 'dayonizeus@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dayonizeus/parsers',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
