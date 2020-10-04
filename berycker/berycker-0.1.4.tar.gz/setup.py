# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['berycker']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.3.1,<0.4.0',
 'paramiko>=2.7.2,<3.0.0',
 'psutil>=5.7.2,<6.0.0',
 'termcolor>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['berycker = berycker.cli:main']}

setup_kwargs = {
    'name': 'berycker',
    'version': '0.1.4',
    'description': '',
    'long_description': None,
    'author': 'Tomoki Murayama',
    'author_email': 'muratomo.0205@gmail.com',
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
