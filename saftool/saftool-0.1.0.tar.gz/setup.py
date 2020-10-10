# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['saftool']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.1,<3.0.0']

setup_kwargs = {
    'name': 'saftool',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': '贾培灵',
    'author_email': 'jiapeiling@yadingdata.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
