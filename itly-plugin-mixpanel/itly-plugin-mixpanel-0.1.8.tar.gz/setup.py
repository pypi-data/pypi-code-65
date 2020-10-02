# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['itly_plugin_mixpanel']

package_data = \
{'': ['*']}

install_requires = \
['itly-sdk>=0.1.0,<0.2.0', 'mixpanel>=4.7.0,<5.0.0']

setup_kwargs = {
    'name': 'itly-plugin-mixpanel',
    'version': '0.1.8',
    'description': 'Iteratively Analytics SDK - Mixpanel Plugin',
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
