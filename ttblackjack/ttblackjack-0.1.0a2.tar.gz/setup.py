# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ttblackjack']

package_data = \
{'': ['*']}

install_requires = \
['toml>=0.10.1,<0.11.0']

entry_points = \
{'console_scripts': ['ttblackjack = ttblackjack.cli:main']}

setup_kwargs = {
    'name': 'ttblackjack',
    'version': '0.1.0a2',
    'description': 'A simple blackjack poker game.',
    'long_description': '# ttblackjack\n\nA simple blackjack poker game.\n\n<img src="images/picture-01.png" width="300" />\n\n## Install\nInstall from `wheel` or PyPI\n```\npip3 install --user ttblackjack\n# or\npipx install ttblackjack\n```\n\n## Help\n```\nttblackjack --help\n```',
    'author': 'JackLPK',
    'author_email': 'puikit.li.jack@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/JackLPK/ttblackjack/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
