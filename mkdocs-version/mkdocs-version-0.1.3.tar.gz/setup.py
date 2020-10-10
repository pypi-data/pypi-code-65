# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mkdocs_version']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0']

entry_points = \
{'console_scripts': ['mkdocs-version = mkdocs_version.commands:main']}

setup_kwargs = {
    'name': 'mkdocs-version',
    'version': '0.1.3',
    'description': 'Simple and easy-to-use mkdocs version based on git tags',
    'long_description': '# mkdocs version\n\n为 [Index.py](https://github.com/abersheeran/index.py) 提供多版本文档支持。\n\n如果你同样使用 Mkdocs，并且项目版本编号类似于 `v1.0.0`，亦可以使用此项目进行多版本的文档生成，使用说明请查看 `mkdocs-version --help`。\n',
    'author': 'abersheeran',
    'author_email': 'me@abersheeran.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/abersheeran/mkdocs-version',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
