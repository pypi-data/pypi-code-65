# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysls', 'pysls.src', 'pysls.utils']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.15.16,<2.0.0']

entry_points = \
{'console_scripts': ['pysls = pysls.src.main:main']}

setup_kwargs = {
    'name': 'pysls',
    'version': '1.0.1',
    'description': '',
    'long_description': None,
    'author': 'LucasFDutra',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
