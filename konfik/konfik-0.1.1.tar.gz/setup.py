# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['konfik']

package_data = \
{'': ['*']}

install_requires = \
['rich>=8.0.0,<9.0.0', 'toml>=0.10.1,<0.11.0']

entry_points = \
{'console_scripts': ['konfik = konfik.main:deploy_cli']}

setup_kwargs = {
    'name': 'konfik',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'rednafi',
    'author_email': 'redowan.nafi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
