# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yards', 'yards.tools']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.19.0,<2.0.0',
 'pillow>=7.2.0,<8.0.0',
 'progressbar2>=3.51.4,<4.0.0',
 'pyyaml>=5.3.1,<6.0.0',
 'tqdm>=4.48.0,<5.0.0']

entry_points = \
{'console_scripts': ['yards = yards._cli:main']}

setup_kwargs = {
    'name': 'yards',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'chanhakim',
    'author_email': 'chanhakim17@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
