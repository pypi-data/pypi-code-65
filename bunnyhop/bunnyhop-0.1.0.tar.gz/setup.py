# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bunnyhop']

package_data = \
{'': ['*']}

install_requires = \
['envs>=1.3,<2.0', 'requests>=2.23.0,<3.0.0', 'valley>=1.5.5,<2.0.0']

setup_kwargs = {
    'name': 'bunnyhop',
    'version': '0.1.0',
    'description': 'A Python library created make building with BunnyCDN easier',
    'long_description': None,
    'author': 'Brian Jinwright',
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
