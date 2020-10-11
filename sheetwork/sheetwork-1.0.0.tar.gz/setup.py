# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sheetwork',
 'sheetwork.core',
 'sheetwork.core.adapters',
 'sheetwork.core.adapters.base',
 'sheetwork.core.clients',
 'sheetwork.core.config',
 'sheetwork.core.task',
 'sheetwork.core.ui',
 'sheetwork.core.yaml']

package_data = \
{'': ['*']}

install_requires = \
['cerberus>=1.3.2,<2.0.0',
 'colorama>=0.4.3,<0.5.0',
 'gspread>=3.3.0,<3.4.0',
 'inflection>=0.5.1,<0.6.0',
 'luddite>=1.0.1,<2.0.0',
 'oauth2client>=4.1.3,<5.0.0',
 'packaging>=20.4,<21.0',
 'pandas>=1.1.2,<1.2.0',
 'pyyaml>=5.3.1,<6.0.0',
 'requests<2.23.0',
 'snowflake-sqlalchemy==1.2.3',
 'sqlalchemy>=1.3.19,<2.0.0']

entry_points = \
{'console_scripts': ['sheetwork = sheetwork.core.main:main']}

setup_kwargs = {
    'name': 'sheetwork',
    'version': '1.0.0',
    'description': 'A handy CLI tool to ingest GoogleSheets into your database without writing a single line of code',
    'long_description': "![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/bastienboutonnet/sheetwork?include_prereleases) [![codecov](https://codecov.io/gh/bastienboutonnet/sheetwork/branch/dev%2Fnicolas_jaar/graph/badge.svg)](https://codecov.io/gh/bastienboutonnet/sheetwork)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n![Sheetwork Build](https://github.com/bastienboutonnet/sheetwork/workflows/Sheetwork%20CI/badge.svg)\n![python](https://img.shields.io/badge/python-3.7%20%7C%203.8-blue)\n[![Discord](https://img.shields.io/discord/752101657218908281?label=discord)](https://discord.gg/ebSTWq)\n# sheetwork 💩🤦\n\nA handy package to load Google Sheets to your database right from the CLI and with easy configuration via YAML files.\n\n> ⚠️ **warning** `sheetwork` is still in its early inception (don't get fooled by the 1 in the version). Please do some testing before you end up using it in production, and feel free to report bugs.\n\n> **compatibility**:\n> - Python >=3.7, Mac OSX >10.14.\n> - Probably works on most UNIX systems but not nested. Most likely absolutely not working in Windows.\n\n🙋🏻\u200d♂️ **Want to use `sheetwork` on other databases? Let's talk!** ([Make an issue](https://github.com/bastienboutonnet/sheetwork/issues/new/choose), or ping me on [Discord](https://discord.gg/5GnNNb))\n\n## Installation & Documentation\n\nHead over to this pretty [documentation](https://bastienboutonnet.gitbook.io/sheetwork/) to get started and find out how to install, and use `sheetwork`\n",
    'author': 'Bastien Boutonnet',
    'author_email': 'bastien.b1@gmail.com',
    'maintainer': 'Bastien Boutonnet',
    'maintainer_email': 'bastien.b1@gmail.com',
    'url': 'https://github.com/bastienboutonnet/sheetwork',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
