# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fast_downloader_mt']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0', 'requests>=2.24.0,<3.0.0', 'rich>=8.0.0,<9.0.0']

entry_points = \
{'console_scripts': ['fdl = fast_downloader_mt.main:fast_downloader']}

setup_kwargs = {
    'name': 'fast-downloader-mt',
    'version': '0.1.0',
    'description': 'Multithreaded fast downloader',
    'long_description': "# Fast Downloader\n\n## Why?\n\nPrimarly, to have a nice tool to download ubuntu packages with apt-fast.\n\n## Documents\n\n#### [CHANGELOG.md](https://github.com/kirozen/fast-downloader/blob/master/CHANGELOG.md)\n#### [LICENSE MIT](https://github.com/kirozen/fast-downloader/blob/master/LICENSE)\n\n\n## Features\n\n- Download multiple files in parallel\n- Partially compatible with aria2 input file format\n\n## Installing\n\nInstall with `pip` or your favorite PyPi package manager.\n\n```shell\npip install fast-downloader-mt\n```\n\n## Dependencies\n\n- Python 3.8+\n- Rich\n- Requests\n- Click\n\n## Usage\n\nUsage: fdl [OPTIONS] [URLS]...\n\nOptions:\n  -t, --threads INTEGER        thread number\n  -i, --input PATH             input file\n  -q, --quiet\n  -d, --destination PATH\n  --aria2-compatibility\n  --buffer-size INTEGER\n  --help                       Show this message and exit.\n\nDefault number of threads set to `cpu_count()`\n\n### Usage with apt-fast\n\nIn `/etc/apt-fast.conf`\n\n```conf\n_DOWNLOADER='fdl --aria2-compatibility -t ${_MAXNUM} -i ${DLLIST} -d ${DLDIR}'\n```\n\n## Dev environment\n\n### Dev dependencies\n\n- pytest\n- pylint\n- black\n- mypy\n- flake8\n- bandit\n- safety\n\n## Setup\n\nWith poetry:\n\n```shell\npoetry install\n```\n",
    'author': 'Kirozen',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kirozen/how-am-i-supposed-to',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
