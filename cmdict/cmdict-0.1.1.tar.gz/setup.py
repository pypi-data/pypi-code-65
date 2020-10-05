# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cmdict']

package_data = \
{'': ['*']}

install_requires = \
['PyMuPDF>=1.17.3,<2.0.0',
 'click>=7.1.2,<8.0.0',
 'colorama>=0.4.3,<0.5.0',
 'loguru>=0.5.1,<0.6.0',
 'requests>=2.24.0,<3.0.0',
 'tqdm>=4.48.0,<5.0.0']

entry_points = \
{'console_scripts': ['cmdict = cmdict:run_script.cli',
                     'cmdicts = cmdict:run_script.search']}

setup_kwargs = {
    'name': 'cmdict',
    'version': '0.1.1',
    'description': 'A command line dictionary toolset',
    'long_description': None,
    'author': 'zequnyu',
    'author_email': 'zequnyu11@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
