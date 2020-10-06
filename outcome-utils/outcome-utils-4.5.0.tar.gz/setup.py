# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['outcome', 'outcome.utils', 'outcome.utils.bin', 'outcome.utils.jinja2']

package_data = \
{'': ['*']}

install_requires = \
['asgiref>=3.2.10,<4.0.0',
 'colored>=1.4.2,<2.0.0',
 'jinja2>=2.11.2,<3.0.0',
 'makefun>=1.9.3,<2.0.0',
 'rich>=6.2,<9.0',
 'semver>=2.10.2,<3.0.0',
 'toml>=0.10.1,<0.11.0']

entry_points = \
{'console_scripts': ['otc-utils = outcome.utils.bin.otc_utils:main']}

setup_kwargs = {
    'name': 'outcome-utils',
    'version': '4.5.0',
    'description': 'A collection of python utils.',
    'long_description': '# utils-py\n![ci-badge](https://github.com/outcome-co/utils-py/workflows/Release/badge.svg?branch=v4.5.0) ![version-badge](https://img.shields.io/badge/version-4.5.0-brightgreen)\n\nA set of python utilities.\n\n## Usage\n\n```sh\npoetry add outcome-utils\n```\n\n## Development\n\nRemember to run `./pre-commit.sh` when you clone the repository.\n',
    'author': 'Douglas Willcocks',
    'author_email': 'douglas@outcome.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/outcome-co/utils-py',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
