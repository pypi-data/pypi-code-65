# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ogscm', 'ogscm.building_blocks']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0',
 'hpccm>=20.9.0,<21.0.0',
 'packaging>=20.4,<21.0',
 'requests>=2.24.0,<3.0.0']

entry_points = \
{'console_scripts': ['ogscm = ogscm.cli:main']}

setup_kwargs = {
    'name': 'ogscm',
    'version': '1.6.0',
    'description': 'OGS Container Maker',
    'long_description': None,
    'author': 'Lars Bilke',
    'author_email': 'lars.bilke@ufz.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.opengeosys.org/ogs/container-maker',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
