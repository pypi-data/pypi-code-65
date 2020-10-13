# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mathlib']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mathlib',
    'version': '0.2.0',
    'description': 'A pure-python maths library',
    'long_description': '<p align="center">\n<a href="https://travis-ci.org/spapanik/mathlib"><img alt="Build" src="https://travis-ci.org/spapanik/mathlib.svg?branch=master"></a>\n<a href="https://coveralls.io/github/spapanik/mathlib"><img alt="Coverage" src="https://coveralls.io/repos/github/spapanik/mathlib/badge.svg?branch=master"></a>\n<a href="https://github.com/spapanik/mathlib/blob/master/LICENSE.txt"><img alt="License" src="https://img.shields.io/github/license/spapanik/mathlib"></a>\n<a href="https://pypi.org/project/mathlib"><img alt="PyPI" src="https://img.shields.io/pypi/v/mathlib"></a>\n<a href="https://pepy.tech/project/mathlib"><img alt="Downloads" src="https://pepy.tech/badge/mathlib"></a>\n<a href="https://github.com/psf/black"><img alt="Code style" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n</p>\n\n# mathlib\n\n_mathlib_ is a pure python mathematics library.\n',
    'author': 'Stephanos Kuma',
    'author_email': 'stephanos@kuma.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/spapanik/mathlib',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.0,<4.0.0',
}


setup(**setup_kwargs)
