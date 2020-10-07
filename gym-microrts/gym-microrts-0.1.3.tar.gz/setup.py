# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gym_microrts', 'gym_microrts.envs']

package_data = \
{'': ['*']}

install_requires = \
['JPype1>=1.0.2,<2.0.0',
 'Pillow>=7.2.0,<8.0.0',
 'dacite>=1.5.1,<2.0.0',
 'gym>=0.17.3,<0.18.0']

setup_kwargs = {
    'name': 'gym-microrts',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'Costa Huang',
    'author_email': 'costa.huang@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
