# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['karafuru']

package_data = \
{'': ['*']}

install_requires = \
['rich>=8.0.0,<9.0.0', 'typer[all]>=0.3.2,<0.4.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=1.6.0,<2.0.0']}

entry_points = \
{'console_scripts': ['karafuru = karafuru.__main__:app']}

setup_kwargs = {
    'name': 'karafuru',
    'version': '0.1.0',
    'description': 'Traditional Chinese colors in your terminal',
    'long_description': '# karafuru\n\n<div align="center">\n\n[![Build status](https://github.com/ChenghaoMou/karafuru/workflows/build/badge.svg?branch=master&event=push)](https://github.com/ChenghaoMou/karafuru/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/karafuru.svg)](https://pypi.org/project/karafuru/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/ChenghaoMou/karafuru/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/ChenghaoMou/karafuru/blob/master/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%F0%9F%9A%80-semantic%20versions-informational.svg)](https://github.com/ChenghaoMou/karafuru/releases)\n[![License](https://img.shields.io/github/license/ChenghaoMou/karafuru)](https://github.com/ChenghaoMou/karafuru/blob/master/LICENSE)\n\nTraditional Chinese karafuru in your terminal\n</div>\n\n## 🚀 Features\n\n<center>\n<img src="https://raw.githubusercontent.com/ChenghaoMou/karafuru/master/colors1.png?token=AHUICOOUND5BUYWKXA3RQGS7P2LG2">\n<img src="https://raw.githubusercontent.com/ChenghaoMou/karafuru/master/colors2.png?token=AHUICOJGAJTXPA6PNEMIFCC7P2LH6">\n<img src="https://raw.githubusercontent.com/ChenghaoMou/karafuru/master/colors3.png?token=AHUICON627KEZ6LKE3T7WXS7P2LI6">\n</center>\n\n## Installation\n\n```bash\npip install karafuru\n```\n\n## Usage\n\n```bash\npython -m karafuru --base [red|blue|green|yellow|black|white|dark|light|metal|all]\n```\n\n## 🛡 License\n\n[![License](https://img.shields.io/github/license/ChenghaoMou/karafuru)](https://github.com/ChenghaoMou/karafuru/blob/master/LICENSE)\n\nThis project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/ChenghaoMou/karafuru/blob/master/LICENSE) for more details.\n\n\n## Credits\n\nThis project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template).\n',
    'author': 'None',
    'author_email': 'mouchenghao@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/karafuru/karafuru',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
