# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fhmake']

package_data = \
{'': ['*']}

install_requires = \
['pdoc3>=0.9.1,<0.10.0', 'tomlkit>=0.7']

extras_require = \
{'full': ['bandit>=1.6.2,<2.0.0',
          'dlint>=0.10.3,<0.11.0',
          'dodgy>=0.2.1,<0.3.0',
          'poetry>=1.1.2,<2.0.0',
          'safety>=1.9.0,<2.0.0']}

entry_points = \
{'console_scripts': ['fhmake = fhmake:cli']}

setup_kwargs = {
    'name': 'fhmake',
    'version': '2020.2',
    'description': 'Provides multiple methods to hide and retrieve data',
    'long_description': '[![Github top language](https://img.shields.io/github/languages/top/FHPythonUtils/FHMake.svg?style=for-the-badge)](../../)\n[![Codacy grade](https://img.shields.io/codacy/grade/ff714fa09a7141ef9f0466073971d853.svg?style=for-the-badge)](https://www.codacy.com/gh/FHPythonUtils/FHMake)\n[![Repository size](https://img.shields.io/github/repo-size/FHPythonUtils/FHMake.svg?style=for-the-badge)](../../)\n[![Issues](https://img.shields.io/github/issues/FHPythonUtils/FHMake.svg?style=for-the-badge)](../../issues)\n[![License](https://img.shields.io/github/license/FHPythonUtils/FHMake.svg?style=for-the-badge)](/LICENSE.md)\n[![Commit activity](https://img.shields.io/github/commit-activity/m/FHPythonUtils/FHMake.svg?style=for-the-badge)](../../commits/master)\n[![Last commit](https://img.shields.io/github/last-commit/FHPythonUtils/FHMake.svg?style=for-the-badge)](../../commits/master)\n[![PyPI Downloads](https://img.shields.io/pypi/dm/fhmake.svg?style=for-the-badge)](https://pypi.org/project/fhmake/)\n[![PyPI Version](https://img.shields.io/pypi/v/fhmake.svg?style=for-the-badge)](https://pypi.org/project/fhmake/)\n\n<!-- omit in toc -->\n# FHMake\n\n<img src="readme-assets/icons/name.png" alt="Project Icon" width="750">\n\nFredHappyface Makefile for python. Run one of the following subcommands:\n\n- install: Poetry install\n- build: Building docs, requirements.txt, setup.py, poetry build\n- security: Run some basic security checks that are not run in vscode\n- publish: Run poetry publish\n\n<!-- omit in toc -->\n## Table of Contents\n- [Changelog](#changelog)\n- [Install With PIP](#install-with-pip)\n- [Language information](#language-information)\n\t- [Built for](#built-for)\n- [Install Python on Windows](#install-python-on-windows)\n\t- [Chocolatey](#chocolatey)\n\t- [Download](#download)\n- [Install Python on Linux](#install-python-on-linux)\n\t- [Apt](#apt)\n- [How to run](#how-to-run)\n\t- [With VSCode](#with-vscode)\n\t- [From the Terminal](#from-the-terminal)\n- [How to update, build and publish](#how-to-update-build-and-publish)\n- [Community Files](#community-files)\n\t- [Licence](#licence)\n\t- [Changelog](#changelog-1)\n\t- [Code of Conduct](#code-of-conduct)\n\t- [Contributing](#contributing)\n\t- [Security](#security)\n\t- [Support](#support)\n\n## Changelog\nSee the [CHANGELOG](/CHANGELOG.md) for more information.\n\n## Install With PIP\n\nInstall dephell first: https://dephell.org/\n\n**"Slim" Build:** Install bandit, dlint, dodgy, poetry, and safety with pipx\n\n```python\npip install fhmake\n```\n\n**Otherwise:**\n```python\npip install fhmake[full]\n```\n\nHead to https://pypi.org/project/fhmake/ for more info\n\n## Language information\n### Built for\nThis program has been written for Python 3 and has been tested with\nPython version 3.8.0 <https://www.python.org/downloads/release/python-380/>.\n\n## Install Python on Windows\n### Chocolatey\n```powershell\nchoco install python\n```\n### Download\nTo install Python, go to <https://www.python.org/> and download the latest\nversion.\n\n## Install Python on Linux\n### Apt\n```bash\nsudo apt install python3.8\n```\n\n## How to run\n### With VSCode\n1. Open the .py file in vscode\n2. Ensure a python 3.8 interpreter is selected (Ctrl+Shift+P > Python:Select\nInterpreter > Python 3.8)\n3. Run by pressing Ctrl+F5 (if you are prompted to install any modules, accept)\n### From the Terminal\n```bash\n./[file].py\n```\n\n## How to update, build and publish\n\n1. Ensure you have installed the following dependencies\n\tLinux\n\t```bash\n\twget dephell.org/install | python3.8\n\twget https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3.8\n\t```\n\tWindows\n\t```powershell\n\t(wget dephell.org/install -UseBasicParsing).Content | python\n\t(wget https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python\n\t```\n2. Use poetry for the heavy lifting and dephell to generate requirements\n\t```bash\n\tpoetry update\n\tdephell deps convert\n\t```\n3. Build/ Publish\n\t```bash\n\tpoetry build\n\tpoetry publish\n\t```\n\tor\n\t```bash\n\tpoetry publish --build\n\t```\n## Community Files\n### Licence\nMIT License\nCopyright (c) FredHappyface\n(See the [LICENSE](/LICENSE.md) for more information.)\n\n### Changelog\nSee the [Changelog](/CHANGELOG.md) for more information.\n\n### Code of Conduct\nIn the interest of fostering an open and welcoming environment, we\nas contributors and maintainers pledge to make participation in our\nproject and our community a harassment-free experience for everyone.\nPlease see the\n[Code of Conduct](https://github.com/FHPythonUtils/.github/blob/master/CODE_OF_CONDUCT.md) for more information.\n\n### Contributing\nContributions are welcome, please see the [Contributing Guidelines](https://github.com/FHPythonUtils/.github/blob/master/CONTRIBUTING.md) for more information.\n\n### Security\nThank you for improving the security of the project, please see the [Security Policy](https://github.com/FHPythonUtils/.github/blob/master/SECURITY.md) for more information.\n\n### Support\nThank you for using this project, I hope it is of use to you. Please be aware that\nthose involved with the project often do so for fun along with other commitments\n(such as work, family, etc). Please see the [Support Policy](https://github.com/FHPythonUtils/.github/blob/master/SUPPORT.md) for more information.\n',
    'author': 'FredHappyface',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/FHPythonUtils/FHMake',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
