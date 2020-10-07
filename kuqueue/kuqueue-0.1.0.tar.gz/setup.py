# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kuqueue']

package_data = \
{'': ['*']}

install_requires = \
['pyrsmq>=0.4.3,<0.5.0', 'redis>=3.5.3,<4.0.0']

setup_kwargs = {
    'name': 'kuqueue',
    'version': '0.1.0',
    'description': 'An easy pythonic redis-based MQ',
    'long_description': None,
    'author': 'Yehonatan Zecharia',
    'author_email': 'yonti95@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
