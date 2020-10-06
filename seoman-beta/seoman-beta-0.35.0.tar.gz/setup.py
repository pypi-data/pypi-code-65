# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['seoman', 'seoman.utils']

package_data = \
{'': ['*']}

install_requires = \
['dateparser>=0.7.6,<0.8.0',
 'google-api-python-client>=1.10.1,<2.0.0',
 'google-auth-oauthlib>=0.4.1,<0.5.0',
 'halo>=0.0.30,<0.0.31',
 'inquirer>=2.7.0,<3.0.0',
 'pyexcelerate>=0.9.0,<0.10.0',
 'pytablewriter>=0.58.0,<0.59.0',
 'requests>=2.24.0,<3.0.0',
 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['seoman = seoman.main:app']}

setup_kwargs = {
    'name': 'seoman-beta',
    'version': '0.35.0',
    'description': 'Beta version for seoman',
    'long_description': None,
    'author': 'ycd',
    'author_email': 'yagizcanilbey1903@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ycd/seoman-beta',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
