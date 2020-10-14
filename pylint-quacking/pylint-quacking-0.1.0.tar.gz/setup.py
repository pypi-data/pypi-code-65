# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylint_quacking']

package_data = \
{'': ['*']}

install_requires = \
['pylint>=2.6.0,<3.0.0']

setup_kwargs = {
    'name': 'pylint-quacking',
    'version': '0.1.0',
    'description': 'Ban annotations. Ducks rule!',
    'long_description': None,
    'author': 'Pete Wildsmith',
    'author_email': 'pete@weargoggles.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
