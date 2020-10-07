# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['format_blocks']

package_data = \
{'': ['*']}

install_requires = \
['typing_extensions>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'format-blocks',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Joseph Atkins-Turkish',
    'author_email': 'spacerat3004@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
