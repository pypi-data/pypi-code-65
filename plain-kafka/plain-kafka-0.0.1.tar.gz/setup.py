# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['plain_kafka']

package_data = \
{'': ['*']}

install_requires = \
['confluent-kafka>=1.5.0,<2.0.0']

setup_kwargs = {
    'name': 'plain-kafka',
    'version': '0.0.1',
    'description': 'Producer and consumer (worker) for kafka',
    'long_description': None,
    'author': 'Alekhin Ivan',
    'author_email': 'i.a.alekhin@gmai.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
