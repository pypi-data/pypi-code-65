# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['itly_plugin_segment']

package_data = \
{'': ['*']}

install_requires = \
['analytics-python>=1.2.9,<2.0.0', 'itly-sdk>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'itly-plugin-segment',
    'version': '0.1.7',
    'description': 'Iteratively Analytics SDK - Segment Plugin',
    'long_description': '',
    'author': 'Iteratively',
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
