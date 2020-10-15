# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['latam', 'latam.caribe', 'latam.centro', 'latam.norte', 'latam.sur']

package_data = \
{'': ['*']}

install_requires = \
['pytz>=2020.1,<2021.0', 'rich>=8.0.0,<9.0.0', 'typer[all]>=0.3.2,<0.4.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=2.0.0,<3.0.0']}

entry_points = \
{'console_scripts': ['latam = latam.__main__:app']}

setup_kwargs = {
    'name': 'latam',
    'version': '0.1.1',
    'description': 'Un paquete para trabajar facilmente con metadatos de paises en latinoamerica.',
    'long_description': '# latam\n\n<div align="center">\n\n[![Build status](https://github.com/tacosdedatos/latam/workflows/build/badge.svg?branch=master&event=push)](https://github.com/tacosdedatos/latam/actions?query=workflow%3Abuild)\n[![Documentation Status](https://readthedocs.org/projects/python-latam/badge/?version=latest)](https://python-latam.readthedocs.io/es/latest/?badge=latest)\n[![Python Version](https://img.shields.io/pypi/pyversions/latam.svg)](https://pypi.org/project/latam/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/tacosdedatos/latam/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/tacosdedatos/latam/blob/master/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%F0%9F%9A%80-semantic%20versions-informational.svg)](https://github.com/tacosdedatos/latam/releases)\n[![License](https://img.shields.io/github/license/tacosdedatos/latam)](https://github.com/tacosdedatos/latam/blob/master/LICENSE)\n\nUn paquete para trabajar facilmente con metadatos de paises en latinoamerica.\n</div>\n\n## ¿Qué trae?\n\n## 📃 Citeishon\n\n```\n@misc{latam,\n  author = {tacosdedatos},\n  title = {Un paquete para trabajar facilmente con metadatos de países de Latinoamérica.},\n  year = {2020},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{https://github.com/tacosdedatos/latam}}\n}\n```\n\n> Este proyecto fue generado con [`python-package-template`](https://github.com/TezRomacH/python-package-template).\n',
    'author': 'tacosdedatos',
    'author_email': 'chekos@tacosdedatos.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tacosdedatos/latam',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
