# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xairos_arc']

package_data = \
{'': ['*']}

install_requires = \
['scapy>=2.4.4,<3.0.0', 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['arc = xairos-arc.cli:main']}

setup_kwargs = {
    'name': 'xairos-arc',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Benjamin Rottke',
    'author_email': 'b.rottke@gmail.com',
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
