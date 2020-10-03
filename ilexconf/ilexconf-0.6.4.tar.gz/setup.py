# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ilexconf', 'ilexconf.tests']

package_data = \
{'': ['*']}

extras_require = \
{'console': ['cleo>=0.8.1,<0.9.0'], 'yaml': ['ruamel.yaml>=0.16.12,<0.17.0']}

setup_kwargs = {
    'name': 'ilexconf',
    'version': '0.6.4',
    'description': 'Configuration library for Python 🔧 Load from multiple sources',
    'long_description': '![ilexconf](https://raw.githubusercontent.com/vduseev/ilexconf/master/docs/img/logo.png)\n\n<h2 align="center">Configuration Library for Python</h2>\n\n<p align="center">\n<a href="https://travis-ci.org/vduseev/ilexconf"><img alt="Build Status" src="https://travis-ci.org/vduseev/ilexconf.svg?branch=master"></a>\n<a href="https://coveralls.io/github/psf/black?branch=master"><img alt="Coverage Status" src="https://coveralls.io/repos/github/psf/black/badge.svg?branch=master"></a>\n<a href="https://github.com/psf/black/blob/master/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>\n<a href="https://pypi.org/project/black/"><img alt="PyPI" src="https://img.shields.io/pypi/v/black"></a>\n<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n</p>\n\n## Features\n\n## Quick Start\n\n## Alternatives\n\n| Library                           | Holly | Dynaconf |\n| --------------------------------- | ----- | -------- |\n| **Read from `.json`**             | x     | x        |\n| **Read from `.toml`**             | x     | x        |\n| **Read from `.ini`**              | x     | x        |\n| **Read from env vars**            | x     | x        |\n| **Read from `.py`**               |       | x        |\n| **Read from `.env`**              |       | x        |\n| **Read from dict object**         | x     |          |\n| **Read from Redis**               |       | x        |\n| **Read from Hashicorp Vault**     |       | x        |\n| **Default values**                | x     | x        |         \n| **Multienvironment**              |       | x        |\n| **Attribute access**              | x     | x        |\n| **Dotted key access**             | x     | x        |\n| **Merging**                       | x     | onelevel |\n| **Interpolation**                 |       | x        |\n| **Saving**                        | x     | x        |\n| **CLI**                           | x     | x        |\n| **Printing**                      | x     | x        |\n| **Validators**                    |       | x        |\n| **Masking sensitive info**        |       | x        |\n| **Django integration**            |       | x        |\n| **Flask integration**             |       | x        |\n| **Hot reload**                    |       |          |\n| *Python 3.6*                      |       |          |\n| *Python 3.7*                      |       |          |\n| *Python 3.8*                      | x     |          |\n\n## Kudos\n\n`ilexconf` heavily borrows from `python-configuration` library and is inspired by it.\n\n## License\n\nMIT',
    'author': 'vduseev',
    'author_email': 'vagiz@duseev.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vduseev/ilexconf',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
