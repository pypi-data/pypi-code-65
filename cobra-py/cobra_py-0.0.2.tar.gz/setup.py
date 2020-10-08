# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cobra_py']

package_data = \
{'': ['*'], 'cobra_py': ['resources/fonts/*']}

install_requires = \
['glooey>=0.3.4,<0.4.0',
 'ipcqueue>=0.9.6,<0.10.0',
 'pillow>=7.2.0,<8.0.0',
 'pyglet>=1.5.7,<2.0.0',
 'pyte>=0.8.0,<0.9.0']

setup_kwargs = {
    'name': 'cobra-py',
    'version': '0.0.2',
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
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
