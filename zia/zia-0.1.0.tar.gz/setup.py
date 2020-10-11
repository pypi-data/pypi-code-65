# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zia']

package_data = \
{'': ['*'], 'zia': ['data/config.yaml']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0', 'requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'zia',
    'version': '0.1.0',
    'description': 'Python SDK for Zscaler Internet Access',
    'long_description': None,
    'author': 'omitroom13',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
