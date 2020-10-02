# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bing_image_urls']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.15.5,<0.16.0']

setup_kwargs = {
    'name': 'bing-image-urls',
    'version': '0.1.0',
    'description': 'fetch bing image urls based on keywords',
    'long_description': None,
    'author': 'ffreemt',
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
