# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['failprint']

package_data = \
{'': ['*']}

install_requires = \
['ansimarkup>=1.4.0,<2.0.0', 'jinja2>=2.11.2,<3.0.0']

extras_require = \
{':sys_platform != "win32"': ['ptyprocess>=0.6.0,<0.7.0']}

entry_points = \
{'console_scripts': ['failprint = failprint.cli:main']}

setup_kwargs = {
    'name': 'failprint',
    'version': '0.6.0',
    'description': 'Run a command, print its output only if it fails.',
    'long_description': '# failprint\n\n[![ci](https://github.com/pawamoy/failprint/workflows/ci/badge.svg)](https://github.com/pawamoy/failprint/actions?query=workflow%3Aci)\n[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://pawamoy.github.io/failprint/)\n[![pypi version](https://img.shields.io/pypi/v/failprint.svg)](https://pypi.org/project/failprint/)\n\nRun a command, print its output only if it fails.\n\nTired of searching the `quiet` options of your programs\nto lighten up the output of your `make check` or `make lint` commands?\n\nTired of finding out that standard output and error are mixed up in some of them?\n\nSimply run your command through `failprint`.\nIf it succeeds, nothing is printed.\nIf it fails, standard error is printed.\nPlus other configuration goodies :wink:\n\n## Example\n\nYou don\'t want to see output when the command succeeds.\n\n![demo](demo.svg)\n\nThe task runner [`duty`](https://github.com/pawamoy/duty) uses `failprint`,\nallowing you to define tasks in Python and run them with minimalist and beautiful output:\n\n![demo_duty](demo_duty.svg)\n\n## Requirements\n\nfailprint requires Python 3.6 or above.\n\n<details>\n<summary>To install Python 3.6, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>\n\n```bash\n# install pyenv\ngit clone https://github.com/pyenv/pyenv ~/.pyenv\n\n# setup pyenv (you should also put these three lines in .bashrc or similar)\nexport PATH="${HOME}/.pyenv/bin:${PATH}"\nexport PYENV_ROOT="${HOME}/.pyenv"\neval "$(pyenv init -)"\n\n# install Python 3.6\npyenv install 3.6.12\n\n# make it available globally\npyenv global system 3.6.12\n```\n</details>\n\n## Installation\n\nWith `pip`:\n```bash\npython3.6 -m pip install failprint\n```\n\nWith [`pipx`](https://github.com/pipxproject/pipx):\n```bash\npython3.6 -m pip install --user pipx\n\npipx install --python python3.6 failprint\n```\n\n## Usage\n\n```console\n% poetry run failprint -h\nusage: failprint [-h] [-c {stdout,stderr,both,none}] [-f {pretty,tap}] [-n NUMBER]\n                 [--no-pty] [--no-progress] [-q] [-s] [-t TITLE] [-z]\n                 COMMAND [COMMAND ...]\n\npositional arguments:\n  COMMAND\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -c {stdout,stderr,both,none}, --capture {stdout,stderr,both,none}\n                        Which output to capture. Colors are supported with \'both\' only,\n                        unless the command has a \'force color\' option.\n  -f {pretty,tap}, --format {pretty,tap}\n                        Output format. Pass your own Jinja2 template as a string with\n                        \'-f custom=TEMPLATE\'. Available variables: command, title\n                        (command or title passed with -t), code (exit status), success\n                        (boolean), failure (boolean), number (command number passed with\n                        -n), output (command output), nofail (boolean), quiet (boolean),\n                        silent (boolean). Available filters: indent (textwrap.indent).\n  -n NUMBER, --number NUMBER\n                        Command number. Useful for the \'tap\' format.\n  --no-pty              Disable the use of a pseudo-terminal. PTY doesn\'t allow programs\n                        to use standard input.\n  --no-progress         Don\'t print any progress while running a command.\n  -q, --quiet           Don\'t print the command output, even if it failed.\n  -s, --silent          Don\'t print anything.\n  -t TITLE, --title TITLE\n                        Command title. Default is the command itself.\n  -z, --zero, --nofail  Don\'t fail. Always return a success (0) exit code.\n```\n\n```python\nfrom failprint.runners import run\n\ncmd = "echo hello"\n\nexit_code = run(\n    cmd,            # str, list of str, or Python callable\n    args=None,      # args for callable\n    kwargs=None,    # kwargs for callable\n    number=1,       # command number, useful for tap format\n    capture=None,   # stdout, stderr, both, none, True or False\n    title=None,     # command title\n    fmt=None,       # pretty, tap, or custom="MY_CUSTOM_FORMAT"\n    pty=False,      # use a PTY\n    progress=True,  # print the "progress" template before running the command\n    nofail=False,   # always return zero\n    quiet=False,    # don\'t print output when the command fails\n    silent=False,   # don\'t print anything\n)\n```',
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
