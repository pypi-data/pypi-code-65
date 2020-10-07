# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wilmes']

package_data = \
{'': ['*']}

install_requires = \
['mechanicalsoup>=0.8', 'python-dateutil>=2.0,<3.0', 'pytz']

entry_points = \
{'console_scripts': ['wilmes = wilmes.__main__:main']}

setup_kwargs = {
    'name': 'wilmes',
    'version': '0.9.1',
    'description': 'Message fetching library for a Finnish school site',
    'long_description': 'Wilmes\n======\n\nWilmes is a message fetching library that can fetch messages from a\npopular Finnish school website.\n',
    'author': 'Tuomas Suutari',
    'author_email': 'tuomas@nepnep.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/suutari/wilmes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
