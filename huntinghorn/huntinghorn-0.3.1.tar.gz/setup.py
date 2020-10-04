# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['huntinghorn']

package_data = \
{'': ['*'], 'huntinghorn': ['data/*']}

install_requires = \
['bullet>=2.2.0,<3.0.0',
 'colorama>=0.4.3,<0.5.0',
 'docopt>=0.6.2,<0.7.0',
 'prompt-toolkit>=3.0.7,<4.0.0']

entry_points = \
{'console_scripts': ['horn = huntinghorn:main']}

setup_kwargs = {
    'name': 'huntinghorn',
    'version': '0.3.1',
    'description': 'Command-Line tool for Hunting Horn users.',
    'long_description': None,
    'author': 'Jeremiah Boby',
    'author_email': 'mail@jeremiahboby.me',
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
