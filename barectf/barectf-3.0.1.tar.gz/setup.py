# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['barectf']

package_data = \
{'': ['*'],
 'barectf': ['include/2/*',
             'include/3/*',
             'schemas/config/2/*',
             'schemas/config/3/*',
             'schemas/config/common/*',
             'templates/*',
             'templates/c/*',
             'templates/metadata/*']}

install_requires = \
['jinja2>=2.11,<3.0',
 'jsonschema>=3.2,<4.0',
 'pyyaml>=5.3,<6.0',
 'setuptools',
 'termcolor>=1.1,<2.0']

entry_points = \
{'console_scripts': ['barectf = barectf.cli:_run']}

setup_kwargs = {
    'name': 'barectf',
    'version': '3.0.1',
    'description': 'Generator of ANSI C tracers which output CTF data streams',
    'long_description': None,
    'author': 'Philippe Proulx',
    'author_email': 'eeppeliteloop@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://barectf.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
