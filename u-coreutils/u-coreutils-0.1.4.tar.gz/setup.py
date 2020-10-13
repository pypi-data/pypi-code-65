# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['u_coreutils', 'u_coreutils.cat', 'u_coreutils.echo']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0']

entry_points = \
{'console_scripts': ['u-cat = u_coreutils.cat:run',
                     'u-echo = u_coreutils.echo:run']}

setup_kwargs = {
    'name': 'u-coreutils',
    'version': '0.1.4',
    'description': 'GNU coreutils implementation with Python 3.8',
    'long_description': '# u-coreutils\n\n![CI](https://github.com/duyixian1234/u-coreutils/workflows/CI/badge.svg?branch=master)\n\nGNU coreutils implementation with Python 3.8\n\n## Tools\n\n✔ cat\n',
    'author': 'duyixian',
    'author_email': 'duyixian1234@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/duyixian1234/u-coreutils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
