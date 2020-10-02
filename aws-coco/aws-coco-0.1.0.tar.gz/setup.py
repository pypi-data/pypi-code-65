# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aws_coco', 'aws_coco.lib']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.15.10,<2.0.0', 'requests>=2.24.0,<3.0.0']

entry_points = \
{'console_scripts': ['coco = aws_coco.main:run']}

setup_kwargs = {
    'name': 'aws-coco',
    'version': '0.1.0',
    'description': 'A utility for managing AWS Console Sessions with Firefox Containers',
    'long_description': None,
    'author': 'Joe Snell',
    'author_email': 'joepsnell@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
