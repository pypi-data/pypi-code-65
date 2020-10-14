# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qrand']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'qrand',
    'version': '0.0.1',
    'description': 'A quantum random number generator for arbitrary probability distributions',
    'long_description': "[![Unitary Fund](https://img.shields.io/badge/Supported_By-UNITARY_FUND-FFF000.svg?style=flat)](http://unitary.fund)\n[![YouTube](https://img.shields.io/badge/PR-qrand-FF0000.svg?style=flat&logo=YouTube&logoColor=white)](https://youtu.be/CG7BxuWFpME)\n[![PyPI](https://img.shields.io/pypi/v/qrand?label=PyPI&style=flat&color=3776AB&logo=Python&logoColor=white)](https://pypi.org/project/qrand/)\n[![MIT License](https://img.shields.io/github/license/pedrorrivero/qrand?label=License&style=flat&color=1D1D1D)](./LICENSE)\n\n\n# qrand\n\n> A quantum random number generator for arbitrary probability distributions\n\nRandom numbers are everywhere.\n\nComputer algorithms, data encryption, physical simulations, and even the arts use them all the time. There is one problem though: it turns out that they are actually very difficult to produce in large amounts. Classical computers can only implement mathematical tricks to emulate randomness, while measuring it out of physical processes turns out to be too slow.\n\nLuckily, the probabilistic nature of quantum computers makes these devices particularly useful for the task. Nonetheless, most of the current efforts in producing quantum random numbers have been focused on uniform probability distributions. Despite this fact, many applications actually need to sample from more complex distributions (e.g. gaussian, poisson).\n\nThis is why I am setting up to develop an easy to use, modular piece of software, capable of producing quantum random numbers from arbitrary distributions. To do so, I will be using mathematical processing alongside IBM's Qiskit framework.\n\n---\n(c) 2020 Pedro Rivero\n",
    'author': 'Pedro Rivero',
    'author_email': 'pedro.rivero.ramirez@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pedrorrivero/qrand',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
