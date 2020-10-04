# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tortoise_gis']

package_data = \
{'': ['*']}

install_requires = \
['shapely>=1.7.1,<2.0.0', 'tortoise-orm>=0.16.14,<0.17.0']

setup_kwargs = {
    'name': 'tortoise-gis',
    'version': '0.1.2',
    'description': 'Geometrical and Geographical support for Tortoise ORM.',
    'long_description': '# Tortoise ORM GIS\n\nThis package is intended to provide support for GIS Operations to Tortoise ORM.\n\nCurrently it only supports PostGIS and **IS NOT** production ready.\n\nRoadmap:\n\n-   [] Support Geometry\n-   [] Support Geography\n-   [] Support SpatiaLite\n\n# License\n\nThis project is licensed under MIT license.\nFor more information, please refer to the `LICENSE` file of the repository.\n',
    'author': 'Eduardo Rezende',
    'author_email': 'eduardorbr7@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/revensky/tortoise-gis',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
