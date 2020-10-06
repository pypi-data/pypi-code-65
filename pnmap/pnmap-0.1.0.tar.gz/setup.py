# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pnmap']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0', 'scapy>=2.4.3,<3.0.0']

entry_points = \
{'console_scripts': ['pnmap = pnmap.console:main']}

setup_kwargs = {
    'name': 'pnmap',
    'version': '0.1.0',
    'description': 'A simplified Python implementation of nmap',
    'long_description': '# pnmap\nA simplified python implementation of nmap\n',
    'author': 'Andrew Stefanich',
    'author_email': 'andrewstefanich@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/veyga/pnmap',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
