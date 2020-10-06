# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lfr',
 'lfr.antlrgen',
 'lfr.compiler',
 'lfr.compiler.constraints',
 'lfr.compiler.language',
 'lfr.fig',
 'lfr.netlistgenerator']

package_data = \
{'': ['*']}

install_requires = \
['antlr4-python3-runtime>=4.8,<5.0',
 'argparse>=1.4.0,<2.0.0',
 'dafd @ /home/krishna/CIDAR/DAFD',
 'networkx>=2.5,<3.0',
 'parchmint @ /home/krishna/CIDAR/pyparchmint',
 'pygraphviz>=1.6,<2.0',
 'pymint @ /home/krishna/CIDAR/pymint']

entry_points = \
{'console_scripts': ['lfr-compile = lfr.cmdline:main']}

setup_kwargs = {
    'name': 'lfr',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Radhakrishna Sanka',
    'author_email': 'rkrishnasanka@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
