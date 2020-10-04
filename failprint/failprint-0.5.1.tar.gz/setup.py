# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['failprint']

package_data = \
{'': ['*']}

install_requires = \
['ansimarkup>=1.4.0,<2.0.0',
 'jinja2>=2.11.2,<3.0.0',
 'ptyprocess>=0.6.0,<0.7.0']

extras_require = \
{'tests': ['mypy>=0.782,<0.783',
           'pytest>=6.0.1,<7.0.0',
           'pytest-cov>=2.10.1,<3.0.0',
           'pytest-randomly>=3.4.1,<4.0.0',
           'pytest-sugar>=0.9.4,<0.10.0',
           'pytest-xdist>=2.1.0,<3.0.0']}

entry_points = \
{'console_scripts': ['failprint = failprint.cli:main']}

setup_kwargs = {
    'name': 'failprint',
    'version': '0.5.1',
    'description': 'Run a command, print its output only if it fails.',
    'long_description': '# failprint\n\n[![ci](https://github.com/pawamoy/failprint/workflows/ci/badge.svg)](https://github.com/pawamoy/failprint/actions?query=workflow%3Aci)\n[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://pawamoy.github.io/failprint/)\n[![pypi version](https://img.shields.io/pypi/v/failprint.svg)](https://pypi.org/project/failprint/)\n\nRun a command, print its output only if it fails.\n\nTired of searching the `quiet` options of your programs\nto lighten up the output of your `make check` or `make lint` commands?\n\nTired of finding out that standard output and error are mixed up in some of them?\n\nSimply run your command through `failprint`.\nIf it succeeds, nothing is printed.\nIf it fails, standard error is printed.\nPlus other configuration goodies :wink:\n\n## Example\n\nSome tools output a lot of things. You don\'t want to see it when the command succeeds.\n\nWithout `failprint`:\n\n- `poetry run bandit -s B404 -r src/`\n- `poetry run black --check $(PY_SRC)`\n\n![basic](https://user-images.githubusercontent.com/3999221/79385294-a2a0e080-7f68-11ea-827d-f72134a02eef.png)\n\nWith `failprint`:\n\n- `poetry run failprint -- bandit -s B404 -r src/`\n- `poetry run failprint -- black --check $(PY_SRC)`\n\n![failprint_fail](https://user-images.githubusercontent.com/3999221/79385302-a5033a80-7f68-11ea-98cd-1f4148629724.png)\n\nIt\'s already better, no? Much more readable!\n\nAnd when everything passes, it\'s even better:\n\n![failprint_success](https://user-images.githubusercontent.com/3999221/79385308-a59bd100-7f68-11ea-8012-90cbe9e0ac08.png)\n\n## Requirements\n\nfailprint requires Python 3.6 or above.\n\n<details>\n<summary>To install Python 3.6, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>\n\n```bash\n# install pyenv\ngit clone https://github.com/pyenv/pyenv ~/.pyenv\n\n# setup pyenv (you should also put these three lines in .bashrc or similar)\nexport PATH="${HOME}/.pyenv/bin:${PATH}"\nexport PYENV_ROOT="${HOME}/.pyenv"\neval "$(pyenv init -)"\n\n# install Python 3.6\npyenv install 3.6.12\n\n# make it available globally\npyenv global system 3.6.12\n```\n</details>\n\n## Installation\n\nWith `pip`:\n```bash\npython3.6 -m pip install failprint\n```\n\nWith [`pipx`](https://github.com/pipxproject/pipx):\n```bash\npython3.6 -m pip install --user pipx\n\npipx install --python python3.6 failprint\n```\n\n## Usage\n\n```\nusage: failprint [-h] [-f {custom,pretty,tap}] [-o {stdout,stderr,combine}] [-n NUMBER] [-t TITLE] COMMAND [COMMAND ...]\n\npositional arguments:\n  COMMAND\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -f {custom,pretty,tap}, --format {custom,pretty,tap}\n                        Output format. Pass your own Jinja2 template as a string with \'-f custom=TEMPLATE\'.\n                        Available variables: title (command or title passed with -t), code (exit status), success (boolean), failure (boolean),\n                        n (command number passed with -n), output (command output). Available filters: indent (textwrap.indent).\n  -o {stdout,stderr,combine}, --output {stdout,stderr,combine}\n                        Which output to use. Colors are supported with \'combine\' only, unless the command has a \'force color\' option.\n  -n NUMBER, --number NUMBER\n                        Command number. Useful for the \'tap\' format.\n  -t TITLE, --title TITLE\n                        Command title. Default is the command itself.\n```\n',
    'author': 'Timothée Mazzucotelli',
    'author_email': 'pawamoy@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pawamoy/failprint',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
