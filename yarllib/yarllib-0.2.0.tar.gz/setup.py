# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['yarllib', 'yarllib.helpers', 'yarllib.models']

package_data = \
{'': ['*']}

install_requires = \
['gym>=0.17.2,<0.18.0',
 'matplotlib>=3.3.2,<4.0.0',
 'numpy>=1.19.2,<2.0.0',
 'pandas>=1.1.2,<2.0.0',
 'scipy>=1.5.2,<2.0.0',
 'seaborn>=0.11.0,<0.12.0']

setup_kwargs = {
    'name': 'yarllib',
    'version': '0.2.0',
    'description': 'Yet Another Reinforcement Learning Library',
    'long_description': '<h1 align="center">\n  <b>yarllib</b>\n</h1>\n\n<p align="center">\n  <a href="https://pypi.org/project/yarllib">\n    <img alt="PyPI" src="https://img.shields.io/pypi/v/yarllib">\n  </a>\n  <a href="https://pypi.org/project/yarllib">\n    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/yarllib" />\n  </a>\n  <a href="">\n    <img alt="PyPI - Status" src="https://img.shields.io/pypi/status/yarllib" />\n  </a>\n  <a href="">\n    <img alt="PyPI - Implementation" src="https://img.shields.io/pypi/implementation/yarllib">\n  </a>\n  <a href="">\n    <img alt="PyPI - Wheel" src="https://img.shields.io/pypi/wheel/yarllib">\n  </a>\n  <a href="https://github.com/marcofavorito/yarllib/blob/master/LICENSE">\n    <img alt="GitHub" src="https://img.shields.io/github/license/marcofavorito/yarllib">\n  </a>\n</p>\n<p align="center">\n  <a href="">\n    <img alt="test" src="https://github.com/marcofavorito/yarllib/workflows/test/badge.svg">\n  </a>\n  <a href="">\n    <img alt="lint" src="https://github.com/marcofavorito/yarllib/workflows/lint/badge.svg">\n  </a>\n  <a href="">\n    <img alt="docs" src="https://github.com/marcofavorito/yarllib/workflows/docs/badge.svg">\n  </a>\n  <a href="https://codecov.io/gh/marcofavorito/yarllib">\n    <img alt="codecov" src="https://codecov.io/gh/marcofavorito/yarllib/branch/master/graph/badge.svg?token=FG3ATGP5P5">\n  </a>\n</p>\n<p align="center">\n  <a href="https://img.shields.io/badge/flake8-checked-blueviolet">\n    <img alt="" src="https://img.shields.io/badge/flake8-checked-blueviolet">\n  </a>\n  <a href="https://img.shields.io/badge/mypy-checked-blue">\n    <img alt="" src="https://img.shields.io/badge/mypy-checked-blue">\n  </a>\n  <a href="https://img.shields.io/badge/code%20style-black-black">\n    <img alt="black" src="https://img.shields.io/badge/code%20style-black-black" />\n  </a>\n  <a href="https://www.mkdocs.org/">\n    <img alt="" src="https://img.shields.io/badge/docs-mkdocs-9cf">\n  </a>\n</p>\n\n\nYet Another Reinforcement Learning Library.\n\nStatus: **development**.\n\n## Why?\n\nI had the need for a RL library/framework that:\n- was clearly and simply implemented, with good enough performances;\n- highly focused on modularity, customizability and extendability;\n- wasn\'t merely Deep Reinforcement Learning oriented.\n\nI couldn\'t find an existing library that satisfied my needs; \nhence I decided to implement _yet another_ RL library.\n\nFor me it is also an opportunity to \nhave a better understanding of the RL algorithms\nand to appreciate the nuances that you can\'t find on a book.\n\nIf you find this repo useful for your research or your project,\nI\'d be very glad :-) don\'t hesitate to reach me out!\n\n## What\n\nThe package is both:\n- a _library_, because it provides off-the-shelf functionalities to\n  set up an RL experiment;\n- a _framework_, because you can compose your custom model by implementing\n  the interfaces, override the default behaviours, or use the existing\n  components as-is.   \n\nYou can find more details in the \n[documentation](https://marcofavorito.github.io/yarllib).\n\n## Tests\n\nTo run tests: `tox`\n\nTo run only the code tests: `tox -e py3.7`\n\nTo run only the linters: \n- `tox -e flake8`\n- `tox -e mypy`\n- `tox -e black-check`\n- `tox -e isort-check`\n\nPlease look at the `tox.ini` file for the full list of supported commands. \n\n## Docs\n\nTo build the docs: `mkdocs build`\n\nTo view documentation in a browser: `mkdocs serve`\nand then go to [http://localhost:8000](http://localhost:8000)\n\n## License\n\nyarllib is released under the GNU Lesser General Public License v3.0 or later (LGPLv3+).\n\nCopyright 2020 Marco Favorito\n\n## Authors\n\n- [Marco Favorito](https://marcofavorito.github.io/)\n\n## Cite\n\nIf you use this library for your research, please consider citing this repository:\n\n```\n@misc{favorito2020,\n  Author = {Marco Favorito},\n  Title = {yarllib: Yet Another Reinforcement Learning Library},\n  Year = {2020},\n}\n```\nAn e-print will come soon :-) \n',
    'author': 'MarcoFavorito',
    'author_email': 'marco.favorito@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://marcofavorito.github.io/yarllib',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
