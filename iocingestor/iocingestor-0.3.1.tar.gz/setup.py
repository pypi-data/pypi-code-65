# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iocingestor',
 'iocingestor.extras',
 'iocingestor.ioc_fanger',
 'iocingestor.operators',
 'iocingestor.sources',
 'iocingestor.whitelists']

package_data = \
{'': ['*'], 'iocingestor.extras': ['public/*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0',
 'aiocontextvars>=0.2.2,<0.3.0',
 'async-exit-stack>=1.0.1,<2.0.0',
 'async-generator>=1.10,<2.0',
 'beautifulsoup4>=4.9.3,<5.0.0',
 'contextvars>=2.4,<3.0',
 'environs>=8.0.0,<9.0.0',
 'fastapi-utils>=0.2.1,<0.3.0',
 'fastapi>=0.61.1,<0.62.0',
 'feedparser>=6.0.1,<7.0.0',
 'importlib-metadata>=1.7.0,<2.0.0',
 'ioc-finder>=5.0.0,<6.0.0',
 'iocextract>=1.13.1,<2.0.0',
 'ipaddress>=1.0.23,<2.0.0',
 'jsonpath-rw>=1.4.0,<2.0.0',
 'loguru>=0.5.3,<0.6.0',
 'poetry-version>=0.1.5,<0.2.0',
 'pydantic>=1.6.1,<2.0.0',
 'pymisp>=2.4.131,<3.0.0',
 'pyparsing>=2.4.7,<3.0.0',
 'requests>=2.24.0,<3.0.0',
 'sgmllib3k>=1.0.0,<2.0.0',
 'statsd>=3.3.0,<4.0.0',
 'twitter>=1.18.0,<2.0.0',
 'uvicorn>=0.12.1,<0.13.0']

entry_points = \
{'console_scripts': ['iocingestor = iocingestor:main']}

setup_kwargs = {
    'name': 'iocingestor',
    'version': '0.3.1',
    'description': 'Extract and aggregate IOCs from threat feeds.',
    'long_description': '# iocingestor\n\n[![PyPI version](https://badge.fury.io/py/iocingestor.svg)](https://badge.fury.io/py/iocingestor)\n[![Build Status](https://travis-ci.com/ninoseki/iocingestor.svg?branch=master)](https://travis-ci.com/ninoseki/iocingestor)\n[![Coverage Status](https://coveralls.io/repos/github/ninoseki/iocingestor/badge.svg?branch=master)](https://coveralls.io/github/ninoseki/iocingestor?branch=master)\n[![CodeFactor](https://www.codefactor.io/repository/github/ninoseki/iocingestor/badge)](https://www.codefactor.io/repository/github/ninoseki/iocingestor)\n\nAn extendable tool to extract and aggregate IoCs from threat feeds.\n\nThis tool is a forked version of [InQuest](https://inquest.net/)\'s [ThreatIngestor](https://github.com/InQuest/ThreatIngestor) focuses on [MISP](https://www.misp-project.org/) integration.\n\n## Key differences\n\n- Better MISP integration.\n  - Working with the latest version of MISP.\n  - Smart event management based on `reference_link`.\n- [MISP warninglist](https://github.com/MISP/misp-warninglists) compatible whitelisting.\n- Using [ioc-finder](https://github.com/fhightower/ioc-finder) instead of [iocextract](https://github.com/InQuest/python-iocextract) for IoC extraction.\n  - YARA rule extraction is dropped.\n\n## Installation\n\niocingestor requires Python 3.6+.\n\nInstall iocingestor from PyPI:\n\n```bash\npip install iocingestor\n```\n\n## Usage\n\nCreate a new `config.yml` file, and configure each source and operator module you want to use. (See `config.example.yml` as a reference.)\n\n```bash\niocingestor config.yml\n```\n\nBy default, it will run forever, polling each configured source every 15 minutes.\n\n## Plugins\n\niocingestor uses a plugin architecture with "source" (input) and "operator" (output) plugins. The currently supported integrations are:\n\n### Sources\n\n- GitHub repository search\n- RSS feeds\n- Twitter\n- Generic web pages\n\n### Operators\n\n- CSV files\n- MISP\n- SQLite database\n',
    'author': 'Manabu Niseki',
    'author_email': 'manabu.niseki@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ninoseki/iocingestor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
