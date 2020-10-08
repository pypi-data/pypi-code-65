# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['SandsPythonFunctions']

package_data = \
{'': ['*']}

install_requires = \
['notebook>=6.0.3,<7.0.0',
 'numpy>=1.18.5,<2.0.0',
 'pandas>=1.0.3,<2.0.0',
 'pyarrow>=0.16.0,<0.17.0',
 'zstandard>=0.13.0,<0.14.0']

setup_kwargs = {
    'name': 'sandspythonfunctions',
    'version': '0.0.1a16',
    'description': 'Functions I use regularly with my python projects',
    'long_description': '# Sands Python Functions\n\n<p align="center">\n<a href="https://github.com/ldsands/SandsPythonFunctions/graphs/commit-activity"><img src="https://img.shields.io/github/commit-activity/m/ldsands/SandsPythonFunctions?style=flat-square"></img></a>\n<a href="https://github.com/ldsands/SandsPythonFunctions/blob/master/LICENSE"><img src="https://img.shields.io/github/license/ldsands/SandsPythonFunctions?style=flat-square"></img></a>\n<img src="https://img.shields.io/github/repo-size/ldsands/SandsPythonFunctions?style=flat-square"></img>\n<img src="https://img.shields.io/github/languages/count/ldsands/SandsPythonFunctions?style=flat-square"></img>\n<a href=""><img src="https://img.shields.io/github/languages/top/ldsands/SandsPythonFunctions?style=flat-square"></img></a>\n<a href="https://github.com/ldsands/SandsPythonFunctions/graphs/commit-activity"><img src="https://img.shields.io/github/commit-activity/m/ldsands/SandsPythonFunctions?style=flat-square"></img></a>\n<a href="https://github.com/ldsands/SandsPythonFunctions/commits/master"><img src="https://img.shields.io/github/last-commit/ldsands/SandsPythonFunctions?style=flat-square"></img></a>\n<a href="https://github.com/ldsands/SandsPythonFunctions/issues?q=is%3Aopen+is%3Aissue"><img src="https://img.shields.io/github/issues-raw/ldsands/SandsPythonFunctions?style=flat-square"></img></a>\n<a href="https://github.com/ldsands/SandsPythonFunctions/issues?q=is%3Aissue+is%3Aclosed"><img src="https://img.shields.io/github/issues-closed/ldsands/SandsPythonFunctions?style=flat-square"></img></a>\n<a href="https://pepy.tech/project/sandspythonfunctions"><img src="https://img.shields.io/pypi/dm/sandspythonfunctions?style=flat-square"></img></a>\n<!-- <a href="https://lgtm.com/projects/g/ldsands/SandsPythonFunctions"><img src="https://img.shields.io/lgtm/grade/python/g/ldsands/SandsPythonFunctions.svg?logo=lgtm&logoWidth=18&style=flat-square"></img></a> -->\n<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square"></a>\n<p>\n\n<!-- <img src="_static/cache/matplotlib_pypi_downloads_badge.svg"/> -->\n<!-- https://img.shields.io/lgtm/grade/python/g/ldsands/SandsPythonFunctions.svg?logo=lgtm&logoWidth=18&style=flat-square -->\n<!-- https://img.shields.io/pypi/dm/sandspythonfunctions?style=flat-square -->\n\nSome functions I find useful regularly and I put them all into one package for easy access\n\nI created this using [Poetry](https://python-poetry.org/).\n\n## Instructions\n\n- To build this you must first install poetry see instructions [here](https://python-poetry.org/docs/#installation)\n- However to make it easy to access this is all of the code you\'ll need on linux to make this run (note that I use zsh not bash for my shell)\n    - First you must navigate to the folder containing these files `CHANGELOG.md   LICENSE  \'README reference.md\'   README.md   dist   poetry.lock   pyproject.toml   src`\n    - You then to make sure that you have the python environment that you want activated\n    - You can then enter the code below\n\n```sh\npoetry build\npoetry install\n```\n\n## Basic Usage Example\n\nTODO:\n\n## Included Packages\n\n### Functions from EmailFunctions\n\n- \n\n### Functions from MultiprocessingFunctions\n\n- \n\n### Functions from ParquetFunctions\n\n- \n\n### Functions from PrintFunctions\n\n- \n\n### Functions from TimerFunctions\n\n- \n\n## CI/CD\n\nSee [this repo](https://github.com/speg03/shishakai/blob/971261e6f73ee8b9dcc83837b6c1a5f809c985f8/.github/workflows/upload-python-package.yml) for an example of someone using poetry with they\'re python project to upload to PyPI on push to master.\n\n## Other Notes About This Code\n\nI use "TESTCODE:" to designate code used in testing functions and scripts. I try to make sure to comment or delete those lines in the release versions of the package\n',
    'author': 'ldsands',
    'author_email': 'ldsands@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ldsands/SandsPythonFunctions',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
