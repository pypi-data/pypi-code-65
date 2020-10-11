# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['u_coreutils']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0']

entry_points = \
{'console_scripts': ['u-cat = u_coreutils.cat:run']}

setup_kwargs = {
    'name': 'u-coreutils',
    'version': '0.1.1',
    'description': 'GNU coreutils implementation with Python 3.8',
    'long_description': None,
    'author': 'duyixian',
    'author_email': 'duyixian1234@qq.com',
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
