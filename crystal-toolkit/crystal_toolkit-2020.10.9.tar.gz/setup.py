# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crystal_toolkit',
 'crystal_toolkit.apps',
 'crystal_toolkit.apps.examples',
 'crystal_toolkit.apps.examples.tests',
 'crystal_toolkit.apps.tests',
 'crystal_toolkit.components',
 'crystal_toolkit.components.transformations',
 'crystal_toolkit.core',
 'crystal_toolkit.core.tests',
 'crystal_toolkit.helpers',
 'crystal_toolkit.renderables']

package_data = \
{'': ['*'], 'crystal_toolkit.apps': ['assets/*']}

install_requires = \
['plotly>=4.10,<5.0', 'pydantic', 'pymatgen>=2020.9.14,<2021.0.0', 'webcolors']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['typing-extensions'],
 'fermi': ['ifermi', 'pyfftw'],
 'server': ['dash>=1.16.3,<2.0.0',
            'dash-daq',
            'gunicorn',
            'redis',
            'Flask-Caching',
            'gevent',
            'dash-mp-components',
            'scikit-learn',
            'robocrys',
            'scikit-image',
            'habanero',
            'hiphive',
            'dscribe',
            'dash-extensions',
            'sentry-sdk']}

setup_kwargs = {
    'name': 'crystal-toolkit',
    'version': '2020.10.9',
    'description': '',
    'long_description': None,
    'author': 'Matthew Horton',
    'author_email': 'mkhorton@lbl.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
