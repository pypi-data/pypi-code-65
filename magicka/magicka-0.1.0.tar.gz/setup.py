# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['magicka', 'magicka._core', 'magicka._test']

package_data = \
{'': ['*']}

install_requires = \
['ply>=3.11,<4.0']

setup_kwargs = {
    'name': 'magicka',
    'version': '0.1.0',
    'description': 'Web automation, made magical',
    'long_description': None,
    'author': 'IgnisDa',
    'author_email': 'ignisda2002@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
