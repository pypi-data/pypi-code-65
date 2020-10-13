# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cobra_py']

package_data = \
{'': ['*'], 'cobra_py': ['resources/fonts/*']}

install_requires = \
['ipcqueue>=0.9.6,<0.10.0',
 'jedi>=0.17.2,<0.18.0',
 'prompt_toolkit>=3.0.7,<4.0.0',
 'pygments>=2.7.1,<3.0.0',
 'pyte>=0.8.0,<0.9.0']

entry_points = \
{'console_scripts': ['sweepleg = cobra_py.repl:run']}

setup_kwargs = {
    'name': 'cobra-py',
    'version': '0.0.3',
    'description': 'An 80s style Python runtime and development environment',
    'long_description': None,
    'author': 'Roberto Alsina',
    'author_email': 'roberto.alsina@gmail.com',
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
