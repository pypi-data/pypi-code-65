# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['cognite', 'cognite.processpool']

package_data = \
{'': ['*']}

install_requires = \
['tblib>=1.6.0,<2.0.0']

setup_kwargs = {
    'name': 'cognite-processpool',
    'version': '0.5.0',
    'description': 'Stable process pool library',
    'long_description': None,
    'author': 'Sander Land',
    'author_email': 'sander.land@cognite.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
