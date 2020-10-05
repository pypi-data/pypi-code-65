# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['web_error', 'web_error.handler']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'web-error',
    'version': '0.1.0',
    'description': 'Web based error utils',
    'long_description': '# Web Errors v0.1.0\n[![image](https://img.shields.io/pypi/v/changelog_gen.svg)](https://pypi.org/project/changelog_gen/)\n[![image](https://img.shields.io/pypi/l/changelog_gen.svg)](https://pypi.org/project/changelog_gen/)\n[![image](https://img.shields.io/pypi/pyversions/changelog_gen.svg)](https://pypi.org/project/changelog_gen/)\n![style](https://github.com/EdgyEdgemond/web-error/workflows/style/badge.svg)\n![tests](https://github.com/EdgyEdgemond/web-error/workflows/tests/badge.svg)\n[![codecov](https://codecov.io/gh/EdgyEdgemond/web-error/branch/master/graph/badge.svg)](https://codecov.io/gh/EdgyEdgemond/web-error)\n\n`web_error` is a set of exceptions and handlers for use in web apis to support easy error management and responses\n\nEach exception easily marshals to JSON for use in api errors. Handlers for different web frameworks are provided.\n',
    'author': 'Daniel Edgecombe',
    'author_email': 'edgy.edgemond@gmail.com',
    'url': 'https://github.com/EdgyEdgemond/web-error/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
