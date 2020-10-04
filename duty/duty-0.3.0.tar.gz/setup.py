# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['duty']

package_data = \
{'': ['*']}

extras_require = \
{'tests': ['coverage>=5.2.1,<6.0.0',
           'invoke>=1.4.1,<2.0.0',
           'mypy>=0.782,<0.783',
           'pytest>=6.0.1,<7.0.0',
           'pytest-cov>=2.10.1,<3.0.0',
           'pytest-randomly>=3.4.1,<4.0.0',
           'pytest-sugar>=0.9.4,<0.10.0',
           'pytest-xdist>=2.1.0,<3.0.0']}

entry_points = \
{'console_scripts': ['duty = duty.cli:main']}

setup_kwargs = {
    'name': 'duty',
    'version': '0.3.0',
    'description': 'A simple task runner.',
    'long_description': '# Duty\n\n[![ci](https://github.com/pawamoy/duty/workflows/ci/badge.svg)](https://github.com/pawamoy/duty/actions?query=workflow%3Aci)\n[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://pawamoy.github.io/duty/)\n[![pypi version](https://img.shields.io/pypi/v/duty.svg)](https://pypi.org/project/duty/)\n\nA simple task runner.\n\n## Requirements\n\nDuty requires Python 3.6 or above.\n\n<details>\n<summary>To install Python 3.6, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>\n\n```bash\n# install pyenv\ngit clone https://github.com/pyenv/pyenv ~/.pyenv\n\n# setup pyenv (you should also put these three lines in .bashrc or similar)\nexport PATH="${HOME}/.pyenv/bin:${PATH}"\nexport PYENV_ROOT="${HOME}/.pyenv"\neval "$(pyenv init -)"\n\n# install Python 3.6\npyenv install 3.6.12\n\n# make it available globally\npyenv global system 3.6.12\n```\n</details>\n\n## Installation\n\nWith `pip`:\n```bash\npython3.6 -m pip install duty\n```\n\nWith [`pipx`](https://github.com/pipxproject/pipx):\n```bash\npython3.6 -m pip install --user pipx\n\npipx install --python python3.6 duty\n```\n',
    'author': 'Timothée Mazzucotelli',
    'author_email': 'pawamoy@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pawamoy/duty',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
