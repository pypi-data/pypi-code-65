# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skydance', 'skydance.tests']

package_data = \
{'': ['*']}

install_requires = \
['pytest-asyncio>=0.14.0,<0.15.0']

setup_kwargs = {
    'name': 'skydance',
    'version': '0.0.1',
    'description': 'A library for communication with Skydance lighting WiFi relay.',
    'long_description': '# Overview\n\nA library for communication with Skydance lighting WiFi relay.\n\n[![Build Status](https://img.shields.io/travis/tomasbedrich/skydance.svg)](https://travis-ci.org/tomasbedrich/skydance)\n[![Coverage Status](https://img.shields.io/coveralls/tomasbedrich/skydance.svg)](https://coveralls.io/r/tomasbedrich/skydance)\n[![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/g/tomasbedrich/skydance.svg)](https://scrutinizer-ci.com/g/tomasbedrich/skydance)\n[![PyPI Version](https://img.shields.io/pypi/v/skydance.svg)](https://pypi.org/project/skydance)\n[![PyPI License](https://img.shields.io/pypi/l/skydance.svg)](https://pypi.org/project/skydance)\n\n# Setup\n\n## Requirements\n\n* Python 3.8+\n\n## Installation\n\nInstall it directly into an activated virtual environment:\n\n```text\n$ pip install skydance\n```\n\nor add it to your [Poetry](https://poetry.eustace.io/) project:\n\n```text\n$ poetry add skydance\n```\n\n# Usage\n\nAfter installation, the package can imported:\n\n```text\n$ python\n>>> import skydance\n>>> skydance.__version__\n```\n',
    'author': 'Tomas Bedrich',
    'author_email': 'ja@tbedrich.cz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/skydance',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
