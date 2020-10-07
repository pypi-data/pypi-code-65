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
    'version': '0.1.1',
    'description': 'An easy pythonic redis-based MQ',
    'long_description': '# kuqueue\n[![Build Status](https://travis-ci.org/yehonatanz/kuqueue.svg?branch=main)](https://travis-ci.org/yehonatanz/kuqueue)\n[![codecov](https://codecov.io/gh/yehonatanz/kuqueue/branch/main/graph/badge.svg?token=01O6IAXMR2)](https://codecov.io/gh/yehonatanz/kuqueue)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nA lightweight, pythonic wrapper around [pyrsmq](https://github.com/mlasevich/PyRSMQ) to expose MQ semantics over vanilla redis\n\nContinuously tested against a recent redis instance and `python>=3.8`\n',
    'author': 'Yehonatan Zecharia',
    'author_email': 'yonti95@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yehonatanz/kuqueue',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
