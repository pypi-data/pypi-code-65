# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kingghidorah']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0', 'requests[socks]>=2.23.0,<3.0.0']

setup_kwargs = {
    'name': 'kingghidorah',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'deepio',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
