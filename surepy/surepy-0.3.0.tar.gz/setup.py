# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['surepy']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6.3,<4.0.0',
 'async-timeout>=3.0.1,<4.0.0',
 'colorama>=0.4.4,<0.5.0']

entry_points = \
{'console_scripts': ['surepy = surepy.cli:cli']}

setup_kwargs = {
    'name': 'surepy',
    'version': '0.3.0',
    'description': 'Library to interact with the flaps & doors from Sure Petcare.',
    'long_description': '# surepy\n\nLibrary to interact with the flaps & doors from Sure Petcare\n',
    'author': 'Ben Lebherz',
    'author_email': 'git@benleb.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/benleb/surepy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
