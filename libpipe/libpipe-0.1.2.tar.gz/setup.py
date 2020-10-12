# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['libpipe', 'libpipe.tests', 'libpipe.tools']

package_data = \
{'': ['*']}

install_requires = \
['asyncssh>=2.0,<3.0',
 'click>=7.0,<8.0',
 'progressbar2>=3.0,<4.0',
 'python-casacore>=3.0,<4.0',
 'tables>=3.2,<4.0',
 'toml>=0.10,<0.11']

entry_points = \
{'console_scripts': ['nodetool = libpipe.tools.nodetool:main']}

setup_kwargs = {
    'name': 'libpipe',
    'version': '0.1.2',
    'description': '',
    'long_description': 'Libpipe\n=======\n\nCommon pipeline framework and library\n\nInstallation\n------------\n\nlibpipe can be installed via pip:\n\n    $ pip install libpipe\n\nand requires Python 3.6.0 or higher.\n',
    'author': '"Florent Mertens"',
    'author_email': '"florent.mertens@gmail.com"',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/flomertens/libpipe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
