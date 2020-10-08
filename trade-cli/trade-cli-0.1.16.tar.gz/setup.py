# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['trade_cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1,<8.0',
 'pick>=0.6.7,<0.7.0',
 'requests>=2.23,<3.0',
 'tabulate>=0.8.7,<0.9.0',
 'tqdm>=4.46,<5.0',
 'windows-curses>=2.1,<3.0']

entry_points = \
{'console_scripts': ['trade-cli = trade_cli.cli:hello']}

setup_kwargs = {
    'name': 'trade-cli',
    'version': '0.1.16',
    'description': '',
    'long_description': None,
    'author': 'Matyi',
    'author_email': 'mmatyi@caesar.elte.hu',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
