# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gym_sapientino',
 'gym_sapientino.core',
 'gym_sapientino.rendering',
 'gym_sapientino.wrappers']

package_data = \
{'': ['*'], 'gym_sapientino': ['assets/*']}

install_requires = \
['gym>=0.17.2,<0.18.0',
 'matplotlib>=3.3.2,<4.0.0',
 'numpy>=1.19.2,<2.0.0',
 'pandas>=1.1.2,<2.0.0',
 'pygame>=2.0.0.dev6',
 'seaborn>=0.11.0,<0.12.0']

setup_kwargs = {
    'name': 'gym-sapientino',
    'version': '0.2.0',
    'description': 'Gym Sapientino environment using Pygame.',
    'long_description': '<h1 align="center">\n  <b>gym-sapientino</b>\n</h1>\n\n<p align="center">\n  <a href="https://pypi.org/project/gym-sapientino">\n    <img alt="PyPI" src="https://img.shields.io/pypi/v/gym-sapientino">\n  </a>\n  <a href="https://pypi.org/project/gym-sapientino">\n    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/gym-sapientino" />\n  </a>\n  <a href="">\n    <img alt="PyPI - Status" src="https://img.shields.io/pypi/status/gym-sapientino" />\n  </a>\n  <a href="">\n    <img alt="PyPI - Implementation" src="https://img.shields.io/pypi/implementation/gym-sapientino">\n  </a>\n  <a href="">\n    <img alt="PyPI - Wheel" src="https://img.shields.io/pypi/wheel/gym-sapientino">\n  </a>\n  <a href="https://github.com/whitemech/gym-sapientino/blob/master/LICENSE">\n    <img alt="GitHub" src="https://img.shields.io/github/license/whitemech/gym-sapientino">\n  </a>\n</p>\n<p align="center">\n  <a href="">\n    <img alt="test" src="https://github.com/whitemech/gym-sapientino/workflows/test/badge.svg">\n  </a>\n  <a href="">\n    <img alt="lint" src="https://github.com/whitemech/gym-sapientino/workflows/lint/badge.svg">\n  </a>\n  <a href="">\n    <img alt="docs" src="https://github.com/whitemech/gym-sapientino/workflows/docs/badge.svg">\n  </a>\n  <a href="https://codecov.io/gh/whitemech/gym-sapientino">\n    <img alt="codecov" src="https://codecov.io/gh/whitemech/gym-sapientino/branch/master/graph/badge.svg?token=FG3ATGP5P5">\n  </a>\n</p>\n<p align="center">\n  <a href="https://img.shields.io/badge/flake8-checked-blueviolet">\n    <img alt="" src="https://img.shields.io/badge/flake8-checked-blueviolet">\n  </a>\n  <a href="https://img.shields.io/badge/mypy-checked-blue">\n    <img alt="" src="https://img.shields.io/badge/mypy-checked-blue">\n  </a>\n  <a href="https://img.shields.io/badge/isort-checked-yellow">\n    <img alt="" src="https://img.shields.io/badge/isort-checked-yellow">\n  </a>\n  <a href="https://img.shields.io/badge/code%20style-black-black">\n    <img alt="black" src="https://img.shields.io/badge/code%20style-black-black" />\n  </a>\n  <a href="https://www.mkdocs.org/">\n    <img alt="" src="https://img.shields.io/badge/docs-mkdocs-9cf">\n  </a>\n</p>\n\nOpenAI Gym Sapientino environment using Pygame.\n\n<p align="center">\n  <img src="https://raw.githubusercontent.com/whitemech/gym-sapientino/master/docs/sapientino-homepage.gif" />\n</p>\n\n## Description\n\nThe environment is inspired by a game for kids called \n[_Sapientino_](https://it.wikipedia.org/wiki/Sapientino).\n \nA robot moves on a gridworld-like environment, \nwhere each cell can be coloured. \nWhen a robot is on a coloured cell, it can \nrun a _beep_, meaning it has visited the cell.\n\nThe environment is compliant with the \n[OpenAI Gym](https://github.com/openai/gym/) APIs.\nThe idea is that the designer of the experiment\nshould implement the actual reward by wrapping the environment. \n\n## Dependencies\n\nThe environment is implemented using Pygame.\n\nOn Ubuntu, you need the following libraries:\n```\nsudo apt-get install python3-dev \\\n    libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev \\\n    libsdl1.2-dev  libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev libfreetype6-dev\n```\n\nOn MacOS (not tested):\n```\nbrew install sdl sdl_ttf sdl_image sdl_mixer portmidi  # brew or use equivalent means\nconda install -c https://conda.binstar.org/quasiben pygame  # using Anaconda\n```\n\n## Install\n\nInstall with `pip`:\n\n    pip install gym_sapientino\n    \nOr, install from source:\n\n    git clone https://github.com/whitemech/gym-sapientino.git\n    cd gym-sapientino\n    pip install .\n\n## Development\n\n- clone the repo:\n```bash\ngit clone https://github.com/whitemech/gym-sapientino.git\ncd gym-sapientino\n```\n    \n- Create/activate the virtual environment:\n```bash\npoetry shell --python=python3.7\n```\n\n- Install development dependencies:\n```bash\npoetry install\n```\n    \n## Tests\n\nTo run tests: `tox`\n\nTo run only the code tests: `tox -e py3.7`\n\nTo run only the linters: \n- `tox -e flake8`\n- `tox -e mypy`\n- `tox -e black-check`\n- `tox -e isort-check`\n\nPlease look at the `tox.ini` file for the full list of supported commands. \n\n## Docs\n\nTo build the docs: `mkdocs build`\n\nTo view documentation in a browser: `mkdocs serve`\nand then go to [http://localhost:8000](http://localhost:8000)\n\n## License\n\ngym-sapientino is released under the GNU General Public License v3.0 or later (GPLv3+).\n\nCopyright 2019-2020 Marco Favorito, Luca Iocchi\n\n## Authors\n\n- [Luca Iocchi](https://sites.google.com/a/dis.uniroma1.it/iocchi/home)\n- [Marco Favorito](https://marcofavorito.github.io/)\n\n## Credits\n\nThe code is largely inspired by [RLGames](https://github.com/iocchi/RLGames.git)\n\nIf you want to use this environment in your research, please consider\nciting this conference paper:\n\n```\n@inproceedings{Giacomo2019FoundationsFR,\n  title={Foundations for Restraining Bolts: Reinforcement Learning with LTLf/LDLf Restraining Specifications},\n  author={Giuseppe De Giacomo and L. Iocchi and Marco Favorito and F. Patrizi},\n  booktitle={ICAPS},\n  year={2019}\n}\n```\n',
    'author': 'Marco Favorito',
    'author_email': 'favorito@diag.uniroma1.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://whitemech.github.io/gym-sapientino',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
