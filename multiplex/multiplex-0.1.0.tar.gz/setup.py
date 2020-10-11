# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['multiplex']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.5.0,<0.6.0',
 'aiostream>=0.4.1,<0.5.0',
 'ansicolors>=1.1.8,<2.0.0',
 'click>=7.1.2,<8.0.0',
 'colorful>=0.5.4,<0.6.0',
 'easy-ansi>=0.3,<0.4',
 'pyte>=0.8.0,<0.9.0']

entry_points = \
{'console_scripts': ['mp = multiplex.main:main']}

setup_kwargs = {
    'name': 'multiplex',
    'version': '0.1.0',
    'description': 'View multiple streams in one interface',
    'long_description': '',
    'author': 'Dan Kilman',
    'author_email': 'dankilman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dankilman/multiplex',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
