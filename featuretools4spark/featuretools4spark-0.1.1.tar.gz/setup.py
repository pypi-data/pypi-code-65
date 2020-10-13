# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['featuretools4spark']

package_data = \
{'': ['*']}

install_requires = \
['featuretools>=0.20.0,<0.21.0', 'pandas>=1.1.3,<2.0.0']

setup_kwargs = {
    'name': 'featuretools4spark',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Weixing Li',
    'author_email': 'weixing.li@verisk.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
