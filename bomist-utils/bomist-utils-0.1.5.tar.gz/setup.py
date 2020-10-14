# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bomist_utils']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['bomist_utils = bomist_utils:cli']}

setup_kwargs = {
    'name': 'bomist-utils',
    'version': '0.1.5',
    'description': 'BOMIST Utilities',
    'long_description': '## BOMIST Utilities\n\n## Getting started\n\nRequirements: Python 3.\n\n```\n$ pip3 install bomist_utils\n$ bomist_utils --help\n```\n\nOn Windows you might have to re-launch your terminal in order for the `bomist_utils` command to be recognized.\n\n## Dumping legacy workspaces (v1 to v2)\n\n```\n$ bomist_utils --dump1 --ws <wspath>\n```\n\n`wspath` is the path of the workspace you want to dump. A `.ws` file must exist in it.\n\nA `legacy.bomist_dump` file will be created on the directory the command is ran from. This file can then be imported by BOMIST v2.\n\n### Limitations\n\nThis utility can only export/dump and keep data connections between:\n\n```\nparts, documents, labels, storage, categories\n```\n\n---\n\nFor more info: [bomist.com](https://bomist.com)\n',
    'author': 'Mario Ribeiro',
    'author_email': 'mario@bomist.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://bomist.com',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
