# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['hermes', 'hermes.templates']

package_data = \
{'': ['*']}

install_requires = \
['chameleon>=3.7.0,<3.8.0', 'pyramid', 'pyramid_chameleon', 'web_error']

entry_points = \
{'paste.app_factory': ['main = hermes.server:main']}

setup_kwargs = {
    'name': 'hermes-pyramid',
    'version': '0.0.0',
    'description': 'Web based reporting api',
    'long_description': '# Hermes Reporting v0.0.0\n[![image](https://img.shields.io/pypi/v/changelog_gen.svg)](https://pypi.org/project/changelog_gen/)\n[![image](https://img.shields.io/pypi/l/changelog_gen.svg)](https://pypi.org/project/changelog_gen/)\n[![image](https://img.shields.io/pypi/pyversions/changelog_gen.svg)](https://pypi.org/project/changelog_gen/)\n![style](https://github.com/EdgyEdgemond/hermes/workflows/style/badge.svg)\n![tests](https://github.com/EdgyEdgemond/hermes/workflows/tests/badge.svg)\n[![codecov](https://codecov.io/gh/EdgyEdgemond/hermes/branch/master/graph/badge.svg)](https://codecov.io/gh/EdgyEdgemond/hermes)\n',
    'author': 'Daniel Edgecombe',
    'author_email': 'edgy.edgemond@gmail.com',
    'url': 'https://github.com/EdgyEdgemond/hermes/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
